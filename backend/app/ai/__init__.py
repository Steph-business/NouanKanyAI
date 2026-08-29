"""
app/ai — Couche GenAI, Copilot Industriel et AI Gateway de NouanKanyAI.

Expose l'ensemble des points d'accès unifiés pour l'interaction avec les LLMs (Google Gemini),
le formatage de contexte industriel, la gestion de mémoire conversationnelle multi-niveaux,
les pipelines RAG et le système d'outils métier (Function Calling).
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
from app.ai.memory import (
    BaseMemory,
    ConversationBufferMemory,
    ConversationMemoryManager,
    ShortTermSessionMemory,
    SummaryMemory,
)
from app.ai.prompt_builder import DEFAULT_SYSTEM_INSTRUCTION, PromptBuilder
from app.ai.prompt_models import BuildingType, MLContext, PromptContext, UserRole
from app.ai.rag import BaseRAGPipeline, IndustrialRAGPipeline
from app.ai.retriever import BaseRetriever, InMemoryRetriever
from app.ai.tools import (
    BaseTool,
    CalculateEnergyCostTool,
    ComparePeriodsTool,
    DetectAnomalyTool,
    GenerateReportTool,
    GetBuildingMetricsTool,
    GetElectricityTariffsTool,
    GetEquipmentDetailsTool,
    GetEnergyHistoryTool,
    GetSensorStatusTool,
    GetWeatherTool,
    PredictConsumptionTool,
    ToolRegistry,
)
from app.ai.types import (
    AIResponse,
    ChatMessage,
    ConfirmedActionRecord,
    DocumentChunk,
    GenerationConfig,
    LongTermEntityMemory,
    MessageRole,
    RecommendationRecord,
    RetrievalResult,
    ToolDefinition,
    ToolResult,
    UserPreferences,
)

__all__ = [
    # Gateway & Assistant
    "AIGateway",
    "IndustrialCopilot",
    # Prompts, Context & Dynamic Models
    "PromptBuilder",
    "DEFAULT_SYSTEM_INSTRUCTION",
    "PromptContext",
    "UserRole",
    "BuildingType",
    "MLContext",
    "IndustrialContextBuilder",
    # Conversation & Sessions
    "ConversationManager",
    "ConversationSession",
    # Memory Subsystem
    "BaseMemory",
    "ConversationBufferMemory",
    "SummaryMemory",
    "ShortTermSessionMemory",
    "ConversationMemoryManager",
    "UserPreferences",
    "RecommendationRecord",
    "ConfirmedActionRecord",
    "LongTermEntityMemory",
    # Tools & Function Calling
    "BaseTool",
    "ToolRegistry",
    "ToolResult",
    "CalculateEnergyCostTool",
    "PredictConsumptionTool",
    "DetectAnomalyTool",
    "GetEnergyHistoryTool",
    "ComparePeriodsTool",
    "GetSensorStatusTool",
    "GetEquipmentDetailsTool",
    "GetBuildingMetricsTool",
    "GenerateReportTool",
    "GetWeatherTool",
    "GetElectricityTariffsTool",
    # Embeddings & Vector Search
    "BaseEmbedder",
    "GeminiEmbedder",
    "MockEmbedder",
    "BaseRetriever",
    "InMemoryRetriever",
    # RAG Pipeline
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
