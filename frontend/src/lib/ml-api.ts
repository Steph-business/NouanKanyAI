/**
 * lib/ml-api.ts — Client API TypeScript typé pour le sous-système Machine Learning de NouanKanyAI.
 * 
 * Permet d'interagir avec les endpoints FastAPI sous /api/v1/ml/* :
 * - Inférence XGBoost (prévision énergétique)
 * - Inférence Isolation Forest (détection d'anomalies)
 * - Diagnostic de santé & monitoring opérationnel
 * - Registre des modèles & journalisation d'audit
 */

import { API_URL } from './api';

// =====================================================================
// Types et Interfaces de Données
// =====================================================================

export interface ForecastingRequest {
  power_kw: number;
  temperature_c?: number;
  hour?: number;
  day_of_week?: number;
  is_weekend?: number;
  is_peak_hour?: number;
  power_kw_lag_1?: number;
  power_kw_lag_6?: number;
  power_kw_lag_24?: number;
  power_rolling_mean?: number;
  power_rolling_std?: number;
  history?: Array<Record<string, any>>;
  strict_bounds?: boolean;
}

export interface PredictionMetadata {
  request_id: string;
  execution_time_ms: number;
  timestamp: string;
  feature_count: number;
  data_hash?: string;
}

export interface PredictionResponse {
  request_id: string;
  prediction: number;
  unit: string;
  model_name: string;
  model_version: string;
  metadata: PredictionMetadata;
}

export interface AnomalyDetectionRequest {
  power_kw: number;
  temperature_c: number;
  vibration_hz: number;
  pressure_bar: number;
  hour?: number;
  power_rolling_std?: number;
  consumption_delta?: number;
  previous_power?: number;
  strict_bounds?: boolean;
}

export type AnomalySeverity = 'normal' | 'faible' | 'modérée' | 'critique';

export interface AnomalyResponse {
  request_id: string;
  is_anomaly: boolean;
  anomaly_score: number;
  anomaly_probability: number;
  confidence: number;
  severity: AnomalySeverity;
  model_name: string;
  model_version: string;
  metadata: PredictionMetadata;
}

export interface ComponentHealthStatus {
  status: 'UP' | 'DOWN' | 'DEGRADED' | 'WARN';
  message?: string;
  latency_ms?: number;
  details?: Record<string, any>;
  forecasting_service?: string;
  anomaly_service?: string;
  loaded_in_memory?: boolean;
  version?: string;
}

export interface MLHealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  models_loaded: boolean;
  registry_loaded: boolean;
  feature_schema_loaded: boolean;
  artifacts_ready: boolean;
  version: string;
  components: Record<string, ComponentHealthStatus>;
  details: {
    check_duration_ms?: number;
    [key: string]: any;
  };
}

export interface MLModelInfo {
  name: string;
  version: string;
  model_type: string;
  status: string;
  trained_at?: string;
  features: string[];
  metrics: Record<string, any>;
  artifact_path?: string;
}

export interface MLUsageMetrics {
  total_requests: number;
  prediction_count: number;
  anomaly_count: number;
  normal_count: number;
  anomaly_rate: number;
  requests_last_minute: number;
  by_model: Record<string, number>;
}

export interface MLPerformanceMetrics {
  avg_execution_time_ms: number;
  min_execution_time_ms: number;
  max_execution_time_ms: number;
  p50_ms: number;
  p95_ms: number;
  p99_ms: number;
  by_model_avg_latency_ms: Record<string, number>;
}

export interface MLReliabilityMetrics {
  error_count: number;
  validation_error_count: number;
  error_rate: number;
  success_rate: number;
  consecutive_errors: number;
  max_consecutive_errors: number;
  last_error_at?: string;
  last_error_message?: string;
  by_model_errors: Record<string, number>;
}

export interface MLRuntimeMetrics {
  usage: MLUsageMetrics;
  performance: MLPerformanceMetrics;
  reliability: MLReliabilityMetrics;
  system: {
    active_model_versions: Record<string, string>;
    last_loaded_at?: string;
    uptime_seconds: number;
  };
}

export interface MLDashboardMetrics {
  timestamp: string;
  health: MLHealthStatus;
  runtime_metrics: MLRuntimeMetrics;
  training_metrics: {
    forecasting: Record<string, any>;
    anomaly_detection: Record<string, any>;
    summary?: string;
  };
  audit_summary: {
    total_audited_transactions: number;
    by_status: Record<string, number>;
    by_operation: Record<string, number>;
    by_model: Record<string, number>;
    avg_latency_ms: number;
  };
}

export interface MLReloadResponse {
  status: string;
  message: string;
  timestamp: string;
  version: string;
  active_models: string[];
}

export interface MLAuditRecord {
  audit_id: string;
  request_id: string;
  timestamp: string;
  operation: string;
  model_name: string;
  model_version: string;
  input_hash?: string;
  input_summary: Record<string, any>;
  output_summary: Record<string, any>;
  execution_time_ms: number;
  status: 'SUCCESS' | 'ERROR' | 'VALIDATION_FAILED';
  error_message?: string;
}

export interface AuditQueryParams {
  limit?: number;
  model_name?: string;
  status?: string;
  operation?: string;
  request_id?: string;
}

export interface MLAPIError {
  success: boolean;
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
    request_id?: string;
  };
}

// =====================================================================
// Fonctions du Client API ML
// =====================================================================

const ML_BASE_URL = `${API_URL}/api/v1/ml`;

/**
 * Gestionnaire générique de requête HTTP avec parsing d'erreur typé.
 */
async function mlFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${ML_BASE_URL}${endpoint}`;
  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      let errorPayload: any = null;
      try {
        errorPayload = await response.json();
      } catch {
        errorPayload = { error: { message: response.statusText } };
      }

      const errorMessage =
        errorPayload?.error?.message ||
        errorPayload?.detail ||
        `Erreur HTTP ${response.status} (${response.statusText})`;

      const error = new Error(errorMessage);
      (error as any).status = response.status;
      (error as any).details = errorPayload?.error?.details || errorPayload;
      (error as any).code = errorPayload?.error?.code || 'HTTP_ERROR';
      throw error;
    }

    return (await response.json()) as T;
  } catch (err: any) {
    console.error(`[ML-API] Erreur sur ${endpoint} :`, err);
    throw err;
  }
}

/**
 * 1. Prévision de la consommation énergétique à t+1 heure (XGBoost).
 */
export async function predictForecasting(payload: ForecastingRequest): Promise<PredictionResponse> {
  return mlFetch<PredictionResponse>('/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * 2. Détection d'anomalies de consommation et vibrations (Isolation Forest).
 */
export async function detectAnomaly(payload: AnomalyDetectionRequest): Promise<AnomalyResponse> {
  return mlFetch<AnomalyResponse>('/detect-anomaly', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * 3. Diagnostic de santé complet du sous-système Machine Learning.
 */
export async function getMLHealth(): Promise<MLHealthStatus> {
  return mlFetch<MLHealthStatus>('/health', {
    method: 'GET',
    cache: 'no-store',
  });
}

/**
 * 4. Liste de tous les modèles ML enregistrés.
 */
export async function getMLModels(): Promise<MLModelInfo[]> {
  return mlFetch<MLModelInfo[]>('/models', {
    method: 'GET',
  });
}

/**
 * 5. Détails d'un modèle spécifique depuis le registre.
 */
export async function getMLModelDetails(modelName: string): Promise<MLModelInfo> {
  return mlFetch<MLModelInfo>(`/models/${encodeURIComponent(modelName)}`, {
    method: 'GET',
  });
}

/**
 * 6. Tableau de bord complet des métriques ML (runtime, entraînement, audit).
 */
export async function getMLMetrics(): Promise<MLDashboardMetrics> {
  return mlFetch<MLDashboardMetrics>('/metrics', {
    method: 'GET',
    cache: 'no-store',
  });
}

/**
 * 7. Rechargement à chaud des modèles (authentifié).
 */
export async function reloadMLModels(apiKey: string = 'dev-admin-key'): Promise<MLReloadResponse> {
  return mlFetch<MLReloadResponse>('/reload', {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey,
    },
  });
}

/**
 * 8. Journal d'audit des transactions d'inférence.
 */
export async function getMLAuditLogs(params?: AuditQueryParams): Promise<MLAuditRecord[]> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.model_name) query.set('model_name', params.model_name);
  if (params?.status) query.set('status', params.status);
  if (params?.operation) query.set('operation', params.operation);
  if (params?.request_id) query.set('request_id', params.request_id);

  const queryString = query.toString() ? `?${query.toString()}` : '';
  return mlFetch<MLAuditRecord[]>(`/audit${queryString}`, {
    method: 'GET',
    cache: 'no-store',
  });
}
