"""Composition root centralisant l'instanciation des adaptateurs et use cases."""

from pathlib import Path

from supabase import Client

from app.application.ports.llm_service import LLMService
from app.application.ports.ml_service import MLService
from app.application.ports.notification_service import NotificationService
from app.application.use_cases.calculate_invoice import CalculateInvoiceUseCase
from app.application.use_cases.detect_anomaly import DetectAnomalyUseCase
from app.application.use_cases.generate_report import GenerateReportUseCase
from app.application.use_cases.predict_consumption import PredictConsumptionUseCase
from app.config.settings import BACKEND_DIR, settings
from app.domain.repositories.machine_repository import MachineRepository
from app.domain.repositories.reading_repository import ReadingRepository
from app.infrastructure.llm.gemini_adapter import GeminiAdapter
from app.infrastructure.ml.combined_adapter import CombinedMLAdapter
from app.infrastructure.ml.isolation_forest_adapter import IsolationForestAdapter
from app.infrastructure.ml.xgboost_adapter import XGBoostAdapter
from app.infrastructure.notifications.console_adapter import ConsoleNotificationAdapter
from app.infrastructure.persistence.demo_repository import (
    DemoMachineRepository,
    DemoReadingRepository,
)
from app.infrastructure.persistence.supabase.client import create_supabase_client
from app.infrastructure.persistence.supabase.machine_repository_impl import (
    SupabaseMachineRepository,
)
from app.infrastructure.persistence.supabase.reading_repository_impl import (
    SupabaseReadingRepository,
)
from app.ml.manager import ModelManager


class Container:
    """Construit une fois les services de l'application, sans connexion à l'import."""

    _instance: "Container | None" = None
    _initialized: bool

    def __new__(cls) -> "Container":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self) -> None:
        """Construit les adaptateurs; Supabase indisponible implique les dépôts démo."""
        if self._initialized:
            return
        self.supabase: Client | None = None
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
            try:
                self.supabase = create_supabase_client()
            except Exception:
                self.supabase = None

        self.machine_repository: MachineRepository
        self.reading_repository: ReadingRepository
        if self.supabase is not None:
            self.machine_repository = SupabaseMachineRepository(self.supabase)
            self.reading_repository = SupabaseReadingRepository(self.supabase)
        else:
            self.machine_repository = DemoMachineRepository()
            self.reading_repository = DemoReadingRepository()

        model_path = Path(settings.ML_MODEL_PATH)
        artifacts_path = model_path if model_path.is_absolute() else BACKEND_DIR / model_path
        self.model_manager = ModelManager(artifacts_dir=artifacts_path)
        self.ml_service: MLService = CombinedMLAdapter(
            XGBoostAdapter(self.model_manager, self.reading_repository),
            IsolationForestAdapter(self.model_manager),
        )
        self.llm_service: LLMService = GeminiAdapter()
        self.notification_service: NotificationService = ConsoleNotificationAdapter()

        self.predict_use_case = PredictConsumptionUseCase(self.machine_repository, self.ml_service)
        self.detect_anomaly_use_case = DetectAnomalyUseCase(
            self.reading_repository, self.ml_service
        )
        self.calculate_invoice_use_case = CalculateInvoiceUseCase()
        self._report_use_case: GenerateReportUseCase | None = None
        self._initialized = True

    @property
    def report_use_case(self) -> GenerateReportUseCase:
        """Construit le générateur de rapports seulement à sa première utilisation."""
        self.initialize()
        if self._report_use_case is None:
            from app.infrastructure.reports.energy_report_adapter import EnergyReportAdapter

            adapter = EnergyReportAdapter()
            self._report_use_case = GenerateReportUseCase(adapter)
        return self._report_use_case

    def load_models(self) -> None:
        """Initialise puis charge les artefacts ML existants."""
        self.initialize()
        self.model_manager.load_models()

    def reset(self) -> None:
        """Réinitialise le singleton pour permettre un remplacement dans les tests."""
        self._initialized = False

    def set_model_manager(self, manager: ModelManager) -> None:
        """Remplace le gestionnaire ML par un faux ou une instance explicite en test."""
        self.initialize()
        self.model_manager = manager
        self.ml_service = CombinedMLAdapter(
            XGBoostAdapter(manager, self.reading_repository),
            IsolationForestAdapter(manager),
        )
        self.predict_use_case = PredictConsumptionUseCase(self.machine_repository, self.ml_service)
        self.detect_anomaly_use_case = DetectAnomalyUseCase(
            self.reading_repository, self.ml_service
        )


container = Container()
