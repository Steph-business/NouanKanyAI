"""
app/ai — Couche GenAI, Copilot Industriel et AI Gateway de NouanKanyAI.

Expose l'ensemble des points d'accès unifiés pour l'interaction avec les LLMs (Google Gemini),
le formatage de contexte industriel, la gestion de mémoire conversationnelle et les pipelines RAG.
"""

from app.ai.assistant import IndustrialCopilot
from app.ai.context import IndustrialContextBuilder
from app.ai.conversation import ConversationManager, ConversationSession
from app.ai.embeddings import BaseEmbedder, GeminiEmbedder, MockEmbedder
from app.ai.exceptions import (
    AIException,
    AIGatewayError,
    AuthenticationError,
    InvalidPromptError,
    MemoryError,
    RAGRetrievalError,
    RateLimitExceededError,
    ToolExecutionError,
)
from app.ai.gateway import AIGateway
from app.ai.memory import BaseMemory, ConversationBufferMemory, SummaryMemory
from app.ai.prompt_builder import DEFAULT_SYSTEM_INSTRUCTION, PromptBuilder
from app.ai.rag import BaseRAGPipeline, IndustrialRAGPipeline
from app.ai.retriever import BaseRetriever, InMemoryRetriever
from app.ai.tools import BaseTool, CalculateEnergyCostTool, ToolRegistry
from app.ai.types import (
    AIResponse,
    ChatMessage,
    DocumentChunk,
    GenerationConfig,
    MessageRole,
    RetrievalResult,
    ToolDefinition,
)

__all__ = [
    # Gateway & Assistant
    "AIGateway",
    "IndustrialCopilot",
    # Prompts & Context
    "PromptBuilder",
    "DEFAULT_SYSTEM_INSTRUCTION",
    "IndustrialContextBuilder",
    # Conversation & Sessions
    "ConversationManager",
    "ConversationSession",
    # Tools & Function Calling
    "BaseTool",
    "ToolRegistry",
    "CalculateEnergyCostTool",
    # Embeddings & Vector Search
    "BaseEmbedder",
    "GeminiEmbedder",
    "MockEmbedder",
    "BaseRetriever",
    "InMemoryRetriever",
    # Memory & RAG
    "BaseMemory",
    "ConversationBufferMemory",
    "SummaryMemory",
    "BaseRAGPipeline",
    "IndustrialRAGPipeline",
    # Types & Contrats
    "MessageRole",
    "ChatMessage",
    "GenerationConfig",
    "AIResponse",
    "ToolDefinition",
    "DocumentChunk",
    "RetrievalResult",
    # Exceptions
    "AIException",
    "AIGatewayError",
    "AuthenticationError",
    "RateLimitExceededError",
    "InvalidPromptError",
    "ToolExecutionError",
    "MemoryError",
    "RAGRetrievalError",
]
