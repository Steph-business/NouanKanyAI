"""
app/ai/prompt_builder.py — Constructeur dynamique de prompts configurable par Jinja2 et YAML.

Assemble dynamiquement et automatiquement les prompts envoyés aux LLMs (Gemini, OpenAI, Anthropic, etc.)
en intégrant :
- Rôle et persona de l'utilisateur (Energy Manager, Directeur, Opérateur, Tech, etc.)
- Type de bâtiment (Industrie, Hôtel, Restaurant, Tertiaire, Grand Ménage)
- Contexte énergétique temps réel et tarification CIE (FCFA)
- Historique de conversation et mémoire utilisateur multi-niveaux
- Résultats d'inférence ML (XGBoost et Isolation Forest)
- Extraits documentaires RAG
- Langue et préférences personnalisées
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import jinja2
import yaml

from app.ai.prompt_models import BuildingType, MLContext, PromptContext, UserRole
from app.ai.types import ChatMessage, DocumentChunk, MessageRole

logger = logging.getLogger("nouankany.ai")

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


# =====================================================================
# Filtres Jinja2 Personnalisés
# =====================================================================

def fcfa_filter(value: Any) -> str:
    """Formate un montant en Francs CFA avec séparateur d'espace."""
    try:
        val = float(value)
        return f"{val:,.0f}".replace(",", " ") + " FCFA"
    except (ValueError, TypeError):
        return f"{value} FCFA"


def kwh_filter(value: Any) -> str:
    """Formate une valeur d'énergie en kWh."""
    try:
        val = float(value)
        return f"{val:,.2f}".replace(",", " ") + " kWh"
    except (ValueError, TypeError):
        return f"{value} kWh"


def severity_filter(value: Any) -> str:
    """Formate un niveau de gravité en badge textuel."""
    sev = str(value).lower()
    badges = {
        "critique": "[CRITIQUE / URGENT]",
        "modérée": "[ATTENTION / MODÉRÉE]",
        "faible": "[MINEURE / FAIBLE]",
        "normal": "[NOMINAL]",
    }
    return badges.get(sev, f"[{sev.upper()}]")


# =====================================================================
# Configurations Par Défaut Embarquées (Fallback)
# =====================================================================

DEFAULT_SYSTEM_INSTRUCTION = """Tu es NouanKanyAI Copilot, l'assistant d'intelligence artificielle expert en gestion et optimisation énergétique pour l'Afrique de l'Ouest (en particulier la Côte d'Ivoire).

Règles de communication :
- Sois rigoureux, concis et factuel.
- Exprime les coûts en FCFA et les puissances en kW / kWh.
- Si des données de machines, prédictions ML ou alertes sont fournies, utilise-les en priorité.
- Propose des actions hiérarchisées d'effacement et de délestage pour éviter les dépassements en heures de pointe CIE (19h-23h).
"""


class PromptBuilder:
    """
    Constructeur modulaire et dynamique de prompts alimenté par Jinja2 et YAML.
    Compatible avec plusieurs fournisseurs de LLM (Gemini, OpenAI, Anthropic, etc.).
    """

    def __init__(
        self,
        templates_dir: Optional[Union[str, Path]] = None,
        system_instruction: Optional[str] = None,
        role_description: Optional[str] = None,
    ) -> None:
        """
        Initialise le moteur de templates de prompts.

        :param templates_dir: Répertoire contenant les fichiers .jinja2 et .yaml.
        :param system_instruction: Instruction système de repli direct si fournie.
        :param role_description: Spécification de rôle optionnelle.
        """
        self.templates_dir = Path(templates_dir) if templates_dir else TEMPLATES_DIR
        self._custom_system_instruction = system_instruction
        self._role_description = role_description

        # 1. Chargement des configurations YAML (Personas & Bâtiments)
        self._roles_config: Dict[str, Any] = self._load_yaml("personas.yaml", default_key="roles")
        self._buildings_config: Dict[str, Any] = self._load_yaml("buildings.yaml", default_key="building_types")

        # 2. Initialisation de l'environnement Jinja2
        template_loaders = []
        if self.templates_dir.exists():
            template_loaders.append(jinja2.FileSystemLoader(str(self.templates_dir)))
        template_loaders.append(jinja2.DictLoader({}))

        self._jinja_env = jinja2.Environment(
            loader=jinja2.ChoiceLoader(template_loaders),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Enregistrement des filtres personnalisés
        self._jinja_env.filters["fcfa"] = fcfa_filter
        self._jinja_env.filters["kwh"] = kwh_filter
        self._jinja_env.filters["severity_badge"] = severity_filter

        logger.debug("[PromptBuilder] Constructeur dynamique Jinja2/YAML initialisé.")

    def _load_yaml(self, filename: str, default_key: str) -> Dict[str, Any]:
        """Charge un fichier YAML de configuration avec fallback sécurisé."""
        path = self.templates_dir / filename
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict) and default_key in data:
                        return data[default_key]
                    return data or {}
            except Exception as e:
                logger.warning(f"[PromptBuilder] Erreur lors du chargement de {filename}: {e}")

        # Fallback minimal si fichier absent
        return {
            "energy_manager": {
                "name": "Responsable Énergie",
                "tone": "technique et orienté KPI",
                "focus": "efficacité et tarification CIE",
                "key_metrics": ["Facture FCFA", "Puissance kW"],
            },
            "industry": {
                "name": "Site Industriel",
                "peak_sensitivity": "TRÈS ÉLEVÉE",
                "cie_contract_type": "Moyenne Tension",
                "recommended_strategy": "Effacement en pointe 19h-23h",
            },
        }

    def register_template(self, template_name: str, template_content: str) -> None:
        """Permet l'enregistrement dynamique d'un template Jinja2 en mémoire."""
        for loader in self._jinja_env.loader.loaders:
            if isinstance(loader, jinja2.DictLoader):
                loader.mapping[template_name] = template_content
                logger.info(f"[PromptBuilder] Template en mémoire '{template_name}' enregistré.")
                return

    def get_supported_roles(self) -> List[str]:
        """Retourne la liste des rôles supportés."""
        return list(self._roles_config.keys())

    def get_supported_building_types(self) -> List[str]:
        """Retourne la liste des types de bâtiments supportés."""
        return list(self._buildings_config.keys())

    def build_system_instruction(
        self,
        context: Optional[Union[PromptContext, Dict[str, Any]]] = None,
        additional_guidelines: Optional[List[str]] = None,
        custom_context: Optional[str] = None,
        memory_context: Optional[str] = None,
    ) -> str:
        """
        Assemble l'instruction système adaptée au persona, au bâtiment et à la langue.

        :param context: Instance de `PromptContext` ou dictionnaire de contexte.
        :param additional_guidelines: Directives impératives optionnelles.
        :param custom_context: Contexte libre d'entreprise.
        :param memory_context: Contexte de mémoire.
        :return: Texte de l'instruction système.
        """
        if self._custom_system_instruction and not context:
            res = self._custom_system_instruction
            if memory_context:
                res += f"\n\n{memory_context}"
            return res.strip()

        # Normalisation du contexte
        ctx_obj = self._ensure_prompt_context(context)

        role_key = (
            ctx_obj.role.value if isinstance(ctx_obj.role, UserRole) else str(ctx_obj.role)
        ).lower()
        bldg_key = (
            ctx_obj.building_type.value
            if isinstance(ctx_obj.building_type, BuildingType)
            else str(ctx_obj.building_type)
        ).lower()

        role_info = self._roles_config.get(
            role_key,
            {
                "name": f"Utilisateur ({role_key})",
                "tone": "professionnel et rigoureux",
                "focus": "gestion de l'énergie",
                "key_metrics": ["Puissance kW", "Coût FCFA"],
            },
        )
        building_info = self._buildings_config.get(
            bldg_key,
            {
                "name": f"Bâtiment ({bldg_key})",
                "peak_sensitivity": "MOYENNE",
                "cie_contract_type": "Standard CIE",
                "recommended_strategy": "Maîtrise de la puissance",
            },
        )

        all_guidelines = list(ctx_obj.additional_instructions or [])
        if additional_guidelines:
            all_guidelines.extend(additional_guidelines)

        render_vars = {
            "language": ctx_obj.language,
            "currency": ctx_obj.currency,
            "role_info": role_info,
            "building_info": building_info,
            "additional_instructions": all_guidelines,
        }

        try:
            template = self._jinja_env.get_template("system_prompt.jinja2")
            rendered = template.render(**render_vars).strip()
        except jinja2.TemplateNotFound:
            rendered = DEFAULT_SYSTEM_INSTRUCTION

        if custom_context:
            rendered += f"\n\nContexte d'entreprise :\n{custom_context}"

        if memory_context:
            rendered += f"\n\n{memory_context}"

        return rendered.strip()

    def format_user_prompt(
        self,
        query: str,
        industrial_context: Optional[str] = None,
        memory_context: Optional[str] = None,
        rag_context: Optional[str] = None,
        ml_context: Optional[Union[MLContext, Dict[str, Any]]] = None,
        context: Optional[PromptContext] = None,
    ) -> str:
        """
        Assemble le prompt utilisateur enrichi de toutes les sources d'information.

        :param query: Requête brute de l'utilisateur.
        :param industrial_context: Télémétrie usine / équipements.
        :param memory_context: Mémoire longue / préférences.
        :param rag_context: Extraits documentaires RAG.
        :param ml_context: Résultats ML (prédiction kW / anomalie).
        :param context: `PromptContext` optionnel.
        :return: Prompt utilisateur formaté.
        """
        # Formater le contexte ML si présent
        ml_dict: Optional[Dict[str, Any]] = None
        if ml_context:
            if isinstance(ml_context, MLContext):
                ml_dict = ml_context.model_dump()
            elif isinstance(ml_context, dict):
                ml_dict = ml_context

        # Formater RAG context si liste de DocumentChunk
        rag_text: Optional[str] = None
        if isinstance(rag_context, list):
            blocks = []
            for c in rag_context:
                if isinstance(c, DocumentChunk):
                    blocks.append(f"- [{c.metadata.get('source', c.document_id)}] {c.content}")
                elif isinstance(c, dict):
                    blocks.append(f"- {c.get('content', str(c))}")
            rag_text = "\n".join(blocks)
        else:
            rag_text = rag_context

        render_vars = {
            "query": query,
            "energy_context": industrial_context,
            "memory_context": memory_context,
            "rag_context": rag_text,
            "ml_context": ml_dict,
        }

        try:
            template = self._jinja_env.get_template("user_prompt.jinja2")
            return template.render(**render_vars).strip()
        except jinja2.TemplateNotFound:
            sections = []
            if memory_context:
                sections.append(f"### [MÉMOIRE & HISTORIQUE DU SITE]\n{memory_context}")
            if industrial_context:
                sections.append(f"### [CONTEXTE INDUSTRIEL TEMPS RÉEL]\n{industrial_context}")
            if ml_dict:
                sections.append(f"### [PRÉVISIONS ET DIAGNOSTIC IA]\n{json.dumps(ml_dict, ensure_ascii=False)}")
            if rag_text:
                sections.append(f"### [DOCUMENTATION TECHNIQUE & PROCÉDURES]\n{rag_text}")
            sections.append(f"### [REQUÊTE DE L'UTILISATEUR]\n{query}")
            return "\n\n".join(sections)

    def create_chat_messages(
        self,
        query: str,
        conversation_history: Optional[List[ChatMessage]] = None,
        industrial_context: Optional[str] = None,
        memory_context: Optional[str] = None,
        rag_context: Optional[str] = None,
        ml_context: Optional[Union[MLContext, Dict[str, Any]]] = None,
    ) -> List[ChatMessage]:
        """
        Assemble la liste chronologique des messages pour la requête de chat.
        """
        messages: List[ChatMessage] = []

        if conversation_history:
            messages.extend(conversation_history)

        formatted_content = self.format_user_prompt(
            query=query,
            industrial_context=industrial_context,
            memory_context=memory_context,
            rag_context=rag_context,
            ml_context=ml_context,
        )

        messages.append(ChatMessage(role=MessageRole.USER, content=formatted_content))
        return messages

    def build_from_prompt_context(self, context: PromptContext) -> tuple[str, List[ChatMessage]]:
        """
        Construit en un seul appel l'instruction système et la liste de messages depuis un `PromptContext`.

        :param context: Instance de `PromptContext`.
        :return: Tuple (system_instruction, chat_messages).
        """
        system_instruction = self.build_system_instruction(context=context)

        # Extraction des contextes annexes
        ind_ctx = str(context.energy_context) if context.energy_context else None
        mem_ctx = str(context.memory_context) if context.memory_context else None
        rag_ctx = str(context.rag_context) if context.rag_context else None

        messages = self.create_chat_messages(
            query=context.query,
            conversation_history=context.conversation_history,
            industrial_context=ind_ctx,
            memory_context=mem_ctx,
            rag_context=rag_ctx,
            ml_context=context.ml_context,
        )

        return system_instruction, messages

    # =====================================================================
    # Adaptateurs Multi-Fournisseurs (Provider Formatters)
    # =====================================================================

    def format_for_provider(
        self,
        messages: List[ChatMessage],
        system_instruction: str,
        provider: str = "gemini",
    ) -> Dict[str, Any]:
        """
        Formate les messages et instructions système pour un fournisseur de LLM spécifique.

        :param messages: Liste de messages `ChatMessage`.
        :param system_instruction: Instruction système.
        :param provider: 'gemini', 'openai', 'anthropic', ou 'raw_text'.
        :return: Structure prête à être sérialisée ou envoyée via SDK/REST.
        """
        prov = provider.lower().strip()

        if prov == "gemini":
            contents = []
            for msg in messages:
                role_str = "user" if msg.role in (MessageRole.USER, MessageRole.SYSTEM) else "model"
                contents.append({"role": role_str, "parts": [{"text": msg.content}]})
            return {
                "contents": contents,
                "systemInstruction": {"parts": [{"text": system_instruction}]},
            }

        elif prov in ("openai", "azure", "mistral", "groq"):
            formatted = [{"role": "system", "content": system_instruction}]
            for msg in messages:
                role_str = "user" if msg.role == MessageRole.USER else ("assistant" if msg.role == MessageRole.ASSISTANT else "system")
                formatted.append({"role": role_str, "content": msg.content})
            return {"messages": formatted}

        elif prov == "anthropic":
            formatted = []
            for msg in messages:
                role_str = "user" if msg.role == MessageRole.USER else "assistant"
                formatted.append({"role": role_str, "content": msg.content})
            return {
                "system": system_instruction,
                "messages": formatted,
            }

        else:  # raw_text / standard
            raw_lines = [f"[SYSTEM]\n{system_instruction}\n"]
            for msg in messages:
                raw_lines.append(f"[{msg.role.value.upper()}]\n{msg.content}\n")
            return {"prompt": "\n".join(raw_lines)}

    def _ensure_prompt_context(
        self, context: Optional[Union[PromptContext, Dict[str, Any]]]
    ) -> PromptContext:
        """Convertit de manière robuste un dictionnaire ou None en `PromptContext`."""
        if isinstance(context, PromptContext):
            return context
        elif isinstance(context, dict):
            return PromptContext(**context)
        return PromptContext(query="")
