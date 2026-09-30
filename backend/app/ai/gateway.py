"""
app/ai/gateway.py — Passerelle centrale et point d'accès unifié aux modèles LLM
(Google Gemini ou Groq).

Centralise tous les appels vers le provider actif (variable d'environnement
AI_PROVIDER="gemini"|"groq", défaut "gemini"), gère les clés d'accès, la
configuration des hyperparamètres de génération, les fallbacks intelligents
pour le développement local, et standardise les objets de réponse avec
métriques de latence — même contrat public (chat/generate_text -> AIResponse)
quel que soit le provider actif.

Groq (https://console.groq.com) : API compatible OpenAI, modèle par défaut
`openai/gpt-oss-20b` — le plus rapide et le seul avec un vrai palier gratuit
sans carte bancaire au moment de l'écriture (30 req/min, 1000 req/jour,
200k tokens/jour ; les modèles Llama sont passés Enterprise-only depuis
août 2026, voir https://console.groq.com/docs/rate-limits). Alternative
utile à Gemini quand aucune dépendance à une machine locale n'est
souhaitable (voir discussion ngrok/Ollama — pas retenue pour cette raison).
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

from app.ai.exceptions import AIGatewayError, AuthenticationError, RateLimitExceededError
from app.ai.types import AIResponse, ChatMessage, GenerationConfig, MessageRole

logger = logging.getLogger("nouankany.ai")


class AIGateway:
    """
    Passerelle unifiée d'accès aux modèles d'IA générative (Google Gemini ou Groq).
    Encapsule la logique d'appel HTTP REST, la gestion d'erreurs et le mode simulation.
    """

    DEFAULT_MODELS = {
        "gemini": "gemini-1.5-flash",
        "groq": "openai/gpt-oss-20b",
    }
    GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        provider: Optional[str] = None,
        timeout_seconds: float = 30.0,
        simulation_mode: Optional[bool] = None,
        fallback_to_simulation: bool = True,
    ) -> None:
        """
        Initialise la passerelle AI.

        :param api_key: Clé API du provider actif (ou lue depuis GEMINI_API_KEY/GROQ_API_KEY).
        :param default_model: Modèle par défaut. Si non fourni, dépend du provider
            (voir DEFAULT_MODELS) — gemini-1.5-flash ou openai/gpt-oss-20b (Groq, gratuit).
        :param provider: "gemini" ou "groq" (ou lu depuis AI_PROVIDER, défaut "gemini").
        :param timeout_seconds: Délai d'expiration des requêtes HTTP en secondes.
        :param simulation_mode: Force le mode simulation sans appel externe si True.
        :param fallback_to_simulation: Bascule automatiquement en simulation si l'API externe échoue.
        """
        self.provider = (provider or os.getenv("AI_PROVIDER", "gemini")).strip().lower()
        if self.provider not in ("gemini", "groq"):
            logger.warning(f"[AIGateway] Provider inconnu '{self.provider}', repli sur 'gemini'.")
            self.provider = "gemini"

        key_env_var = "GEMINI_API_KEY" if self.provider == "gemini" else "GROQ_API_KEY"
        raw_key = api_key if api_key is not None else os.getenv(key_env_var, "")
        self.api_key = raw_key.strip()
        self.default_model = default_model or self.DEFAULT_MODELS[self.provider]
        self.timeout_seconds = timeout_seconds
        self.fallback_to_simulation = fallback_to_simulation

        # Si simulation_mode est forcé ou si la clé est absente / factice
        is_dummy_key = (
            not self.api_key
            or "your" in self.api_key.lower()
            or "dummy" in self.api_key.lower()
            or "test" in self.api_key.lower()
            or len(self.api_key) < 15
        )
        self.is_simulation_mode = simulation_mode if simulation_mode is not None else is_dummy_key

        if self.is_simulation_mode:
            logger.warning(
                f"[AIGateway] Mode simulation actif (provider={self.provider}, réponses synthétiques locales)."
            )
        else:
            logger.info(
                f"[AIGateway] Initialisé avec succès (provider={self.provider}, modèle par défaut: {self.default_model})."
            )

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
        model_name: Optional[str] = None,
    ) -> AIResponse:
        """
        Génère une complétion textuelle simple à partir d'un prompt.

        :param prompt: Invite textuelle pour le modèle.
        :param system_instruction: Directive système optionnelle (rôle, contraintes).
        :param config: Paramètres de génération (température, top_p, max_tokens).
        :param model_name: Modèle cible optionnel.
        :return: Instance typée `AIResponse`.
        """
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        return self.chat(
            messages=messages,
            system_instruction=system_instruction,
            config=config,
            model_name=model_name,
        )

    def chat(
        self,
        messages: List[ChatMessage],
        system_instruction: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        config: Optional[GenerationConfig] = None,
        model_name: Optional[str] = None,
    ) -> AIResponse:
        """
        Génère une réponse dans le cadre d'une conversation multi-tours.

        :param messages: Liste chronologique des messages de la conversation.
        :param system_instruction: Directive système globale.
        :param tools: Liste de déclarations de fonctions (Function Calling).
        :param config: Configuration de génération.
        :param model_name: Modèle à utiliser.
        :return: Instance typée `AIResponse`.
        """
        active_model = model_name or self.default_model
        gen_config = config or GenerationConfig()
        start_time = time.perf_counter()

        logger.debug(
            f"[AIGateway] Envoi requête chat (provider={self.provider}, modèle={active_model}, "
            f"messages={len(messages)}, simulation={self.is_simulation_mode})"
        )

        if self.is_simulation_mode:
            return self._simulate_response(
                messages=messages,
                system_instruction=system_instruction,
                model_name=active_model,
                start_time=start_time,
            )

        if self.provider == "groq":
            endpoint_url = self.GROQ_API_URL
            payload = self._build_groq_payload(
                messages=messages,
                system_instruction=system_instruction,
                tools=tools,
                config=gen_config,
                model=active_model,
            )
            # Groq est compatible OpenAI : Authorization: Bearer <clé>, jamais en
            # query string — même principe que x-goog-api-key côté Gemini.
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                # Sans User-Agent explicite, urllib envoie "Python-urllib/x.y",
                # que le pare-feu Cloudflare devant api.groq.com bloque en 403
                # (error code 1010, "signature de navigateur" suspecte) — vu en
                # test réel, curl passe sans ce souci avec son propre UA.
                "User-Agent": "NouanKanyAI-Backend/1.0",
            }
        else:
            endpoint_url = f"{self.GEMINI_API_BASE_URL}/{active_model}:generateContent"
            payload = self._build_gemini_payload(
                messages=messages,
                system_instruction=system_instruction,
                tools=tools,
                config=gen_config,
            )
            # La clé API part en en-tête (x-goog-api-key), jamais dans l'URL : une
            # clé en query string finit tôt ou tard dans un log d'accès, un message
            # d'exception ou un outil de tracing qui capture l'URL de la requête.
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            }

        provider_label = "Groq" if self.provider == "groq" else "Gemini"

        try:
            req_data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(
                endpoint_url,
                data=req_data,
                headers=headers,
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))

            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            if self.provider == "groq":
                return self._parse_groq_response(resp_data, active_model, latency_ms)
            return self._parse_gemini_response(resp_data, active_model, latency_ms)

        except urllib.error.HTTPError as http_err:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            status_code = http_err.code
            err_body = http_err.read().decode("utf-8", errors="replace")
            logger.error(
                f"[AIGateway] Erreur HTTP {status_code} de l'API {provider_label} : {err_body}"
            )

            if self.fallback_to_simulation:
                logger.warning(
                    f"[AIGateway] Repli automatique sur le mode simulation suite à l'erreur HTTP {status_code}."
                )
                return self._simulate_response(
                    messages=messages,
                    system_instruction=system_instruction,
                    model_name=active_model,
                    start_time=start_time,
                )

            if status_code in (401, 403):
                raise AuthenticationError(
                    f"Clé API {provider_label} non autorisée ou expirée (HTTP {status_code}).",
                    details={"body": err_body},
                ) from http_err
            elif status_code == 429:
                raise RateLimitExceededError(
                    f"Quota d'appels {provider_label} dépassé (HTTP 429).",
                    details={"body": err_body},
                ) from http_err
            else:
                raise AIGatewayError(
                    f"Erreur de communication avec {provider_label} (HTTP {status_code}) : {http_err.reason}",
                    details={"body": err_body, "status_code": status_code},
                ) from http_err

        except Exception as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            logger.error(f"[AIGateway] Exception lors de l'appel {provider_label} : {e}")
            if self.fallback_to_simulation:
                logger.warning(
                    f"[AIGateway] Repli automatique sur le mode simulation suite à l'exception : {e}"
                )
                return self._simulate_response(
                    messages=messages,
                    system_instruction=system_instruction,
                    model_name=active_model,
                    start_time=start_time,
                )
            raise AIGatewayError(
                f"Échec de l'appel à la passerelle IA : {str(e)}",
                details={"model": active_model, "latency_ms": latency_ms},
            ) from e

    def _build_gemini_payload(
        self,
        messages: List[ChatMessage],
        system_instruction: Optional[str],
        tools: Optional[List[Dict[str, Any]]],
        config: GenerationConfig,
    ) -> Dict[str, Any]:
        """Construit le payload JSON conforme à l'API Google Gemini REST v1beta."""
        contents = []
        for msg in messages:
            role_str = "user" if msg.role in (MessageRole.USER, MessageRole.SYSTEM) else "model"
            contents.append({
                "role": role_str,
                "parts": [{"text": msg.content}],
            })

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": config.temperature,
                "topP": config.top_p,
                "topK": config.top_k,
                "maxOutputTokens": config.max_output_tokens,
            },
        }

        if config.stop_sequences:
            payload["generationConfig"]["stopSequences"] = config.stop_sequences

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        if tools:
            payload["tools"] = [{"functionDeclarations": tools}]

        return payload

    def _parse_gemini_response(
        self, resp_data: Dict[str, Any], model_name: str, latency_ms: float
    ) -> AIResponse:
        """Parse et normalise la réponse brute de l'API Gemini."""
        candidates = resp_data.get("candidates", [])
        if not candidates:
            raise AIGatewayError(
                "L'API Gemini n'a renvoyé aucun candidat dans sa réponse.",
                details={"response": resp_data},
            )

        candidate = candidates[0]
        content_obj = candidate.get("content", {})
        parts = content_obj.get("parts", [])
        text_parts = [p.get("text", "") for p in parts if "text" in p]
        content_text = "".join(text_parts).strip()
        finish_reason = candidate.get("finishReason", "STOP")

        usage = resp_data.get("usageMetadata", {})
        usage_tokens = {
            "prompt_tokens": usage.get("promptTokenCount", 0),
            "completion_tokens": usage.get("candidatesTokenCount", 0),
            "total_tokens": usage.get("totalTokenCount", 0),
        }

        return AIResponse(
            content=content_text,
            model_name=model_name,
            latency_ms=latency_ms,
            finish_reason=finish_reason,
            usage_tokens=usage_tokens,
            raw_response=resp_data,
        )

    def _build_groq_payload(
        self,
        messages: List[ChatMessage],
        system_instruction: Optional[str],
        tools: Optional[List[Dict[str, Any]]],
        config: GenerationConfig,
        model: str,
    ) -> Dict[str, Any]:
        """Construit le payload JSON conforme à l'API Groq (compatible OpenAI Chat Completions)."""
        chat_messages: List[Dict[str, str]] = []
        if system_instruction:
            chat_messages.append({"role": "system", "content": system_instruction})
        for msg in messages:
            role_str = "assistant" if msg.role == MessageRole.ASSISTANT else "user"
            chat_messages.append({"role": role_str, "content": msg.content})

        payload: Dict[str, Any] = {
            "model": model,
            "messages": chat_messages,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_tokens": config.max_output_tokens,
        }

        if config.stop_sequences:
            payload["stop"] = config.stop_sequences

        if tools:
            # `tools` est déjà au format OpenAI ici (ToolRegistry.get_openai_schemas(),
            # voir app/ai/assistant.py qui choisit le format selon le provider actif) :
            # {"name","description","parameters"} -> {"type":"function","function":{...}}.
            payload["tools"] = [
                {"type": "function", "function": t} if "type" not in t else t
                for t in tools
            ]

        return payload

    def _parse_groq_response(
        self, resp_data: Dict[str, Any], model_name: str, latency_ms: float
    ) -> AIResponse:
        """Parse et normalise la réponse brute de l'API Groq (format OpenAI Chat Completions)."""
        choices = resp_data.get("choices", [])
        if not choices:
            raise AIGatewayError(
                "L'API Groq n'a renvoyé aucun choix dans sa réponse.",
                details={"response": resp_data},
            )

        choice = choices[0]
        message = choice.get("message", {})
        content_text = (message.get("content") or "").strip()
        finish_reason = (choice.get("finish_reason") or "stop").upper()

        tool_calls = message.get("tool_calls")

        usage = resp_data.get("usage", {})
        usage_tokens = {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

        return AIResponse(
            content=content_text,
            model_name=resp_data.get("model", model_name),
            latency_ms=latency_ms,
            finish_reason=finish_reason,
            usage_tokens=usage_tokens,
            tool_calls=tool_calls,
            raw_response=resp_data,
        )

    def _simulate_response(
        self,
        messages: List[ChatMessage],
        system_instruction: Optional[str],
        model_name: str,
        start_time: float,
    ) -> AIResponse:
        """Fournit une réponse contextuelle réaliste en mode hors-ligne sans clé API."""
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        last_user_msg = ""
        for m in reversed(messages):
            if m.role == MessageRole.USER:
                last_user_msg = m.content
                break

        simulated_text = (
            f"[NouanKanyAI Copilot - Mode Local] "
            f"Analyse industrielle pour la requête : \"{last_user_msg}\". "
            f"La consommation énergétique globale est sous contrôle nominal."
        )

        return AIResponse(
            content=simulated_text,
            model_name=f"{model_name}-simulated",
            latency_ms=latency_ms,
            finish_reason="STOP",
            usage_tokens={"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
        )
