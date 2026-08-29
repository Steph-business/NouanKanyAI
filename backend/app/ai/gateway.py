"""
app/ai/gateway.py — Passerelle centrale et point d'accès unifié aux modèles LLM (Google Gemini).

Centralise tous les appels vers l'API Gemini, gère les clés d'accès, la configuration
des hyperparamètres de génération, les fallbacks intelligents pour le développement local,
et standardise les objets de réponse avec métriques de latence.
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
    Passerelle unifiée d'accès aux modèles d'IA générative (Google Gemini).
    Encapsule la logique d'appel HTTP REST, la gestion d'erreurs et le mode simulation.
    """

    DEFAULT_MODEL = "gemini-1.5-flash"
    API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = DEFAULT_MODEL,
        timeout_seconds: float = 30.0,
        simulation_mode: Optional[bool] = None,
        fallback_to_simulation: bool = True,
    ) -> None:
        """
        Initialise la passerelle AI.

        :param api_key: Clé API Google Gemini (ou lue depuis GEMINI_API_KEY).
        :param default_model: Modèle par défaut (ex: gemini-1.5-flash, gemini-1.5-pro).
        :param timeout_seconds: Délai d'expiration des requêtes HTTP en secondes.
        :param simulation_mode: Force le mode simulation sans appel externe si True.
        :param fallback_to_simulation: Bascule automatiquement en simulation si l'API externe échoue.
        """
        raw_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")
        self.api_key = raw_key.strip()
        self.default_model = default_model
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
                "[AIGateway] Mode simulation actif (réponses synthétiques locales)."
            )
        else:
            logger.info(
                f"[AIGateway] Initialisé avec succès (modèle par défaut: {self.default_model})."
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
            f"[AIGateway] Envoi requête chat (modèle={active_model}, "
            f"messages={len(messages)}, simulation={self.is_simulation_mode})"
        )

        if self.is_simulation_mode:
            return self._simulate_response(
                messages=messages,
                system_instruction=system_instruction,
                model_name=active_model,
                start_time=start_time,
            )

        # Construction du payload Gemini API
        payload = self._build_gemini_payload(
            messages=messages,
            system_instruction=system_instruction,
            tools=tools,
            config=gen_config,
        )

        endpoint_url = f"{self.API_BASE_URL}/{active_model}:generateContent?key={self.api_key}"

        try:
            req_data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(
                endpoint_url,
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))

            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return self._parse_gemini_response(resp_data, active_model, latency_ms)

        except urllib.error.HTTPError as http_err:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            status_code = http_err.code
            err_body = http_err.read().decode("utf-8", errors="replace")
            logger.error(
                f"[AIGateway] Erreur HTTP {status_code} de l'API Gemini : {err_body}"
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
                    f"Clé API Gemini non autorisée ou expirée (HTTP {status_code}).",
                    details={"body": err_body},
                ) from http_err
            elif status_code == 429:
                raise RateLimitExceededError(
                    "Quota d'appels Gemini dépassé (HTTP 429).",
                    details={"body": err_body},
                ) from http_err
            else:
                raise AIGatewayError(
                    f"Erreur de communication avec Gemini (HTTP {status_code}) : {http_err.reason}",
                    details={"body": err_body, "status_code": status_code},
                ) from http_err

        except Exception as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            logger.error(f"[AIGateway] Exception lors de l'appel Gemini : {e}")
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
