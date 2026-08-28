'use client';

/**
 * hooks/use-ml.ts — Hooks React personnalisés pour la consommation de l'API Machine Learning.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  ForecastingRequest,
  PredictionResponse,
  AnomalyDetectionRequest,
  AnomalyResponse,
  MLHealthStatus,
  MLDashboardMetrics,
  MLModelInfo,
  MLAuditRecord,
  AuditQueryParams,
  predictForecasting,
  detectAnomaly,
  getMLHealth,
  getMLMetrics,
  getMLModels,
  getMLAuditLogs,
  reloadMLModels,
} from '@/lib/ml-api';

// =====================================================================
// 1. Hook : usePrediction (Prévision XGBoost)
// =====================================================================

export function usePrediction() {
  const [data, setData] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const predict = useCallback(async (payload: ForecastingRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await predictForecasting(payload);
      setData(res);
      return res;
    } catch (err: any) {
      const msg = err.message || "Échec de la prédiction énergétique.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, predict, reset };
}

// =====================================================================
// 2. Hook : useAnomalyDetection (Isolation Forest)
// =====================================================================

export function useAnomalyDetection() {
  const [data, setData] = useState<AnomalyResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const scan = useCallback(async (payload: AnomalyDetectionRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await detectAnomaly(payload);
      setData(res);
      return res;
    } catch (err: any) {
      const msg = err.message || "Échec de l'analyse d'anomalie.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, scan, reset };
}

// =====================================================================
// 3. Hook : useMLHealth (Diagnostic & Santé avec polling)
// =====================================================================

export function useMLHealth(options?: { pollingInterval?: number; enabled?: boolean }) {
  const { pollingInterval = 10000, enabled = true } = options || {};
  const [health, setHealth] = useState<MLHealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const isMounted = useRef<boolean>(true);

  const fetchHealth = useCallback(async () => {
    try {
      const res = await getMLHealth();
      if (isMounted.current) {
        setHealth(res);
        setError(null);
      }
    } catch (err: any) {
      if (isMounted.current) {
        setError(err.message || 'Impossible de contacter le sous-système ML.');
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    isMounted.current = true;
    if (!enabled) return;

    fetchHealth();
    const interval = setInterval(fetchHealth, pollingInterval);

    return () => {
      isMounted.current = false;
      clearInterval(interval);
    };
  }, [fetchHealth, pollingInterval, enabled]);

  return { health, loading, error, refresh: fetchHealth };
}

// =====================================================================
// 4. Hook : useMLMetrics (Tableau de bord métriques temps réel)
// =====================================================================

export function useMLMetrics(options?: { pollingInterval?: number; enabled?: boolean }) {
  const { pollingInterval = 5000, enabled = true } = options || {};
  const [metrics, setMetrics] = useState<MLDashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const isMounted = useRef<boolean>(true);

  const fetchMetrics = useCallback(async () => {
    try {
      const res = await getMLMetrics();
      if (isMounted.current) {
        setMetrics(res);
        setError(null);
      }
    } catch (err: any) {
      if (isMounted.current) {
        setError(err.message || 'Erreur lors du chargement des métriques ML.');
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    isMounted.current = true;
    if (!enabled) return;

    fetchMetrics();
    const interval = setInterval(fetchMetrics, pollingInterval);

    return () => {
      isMounted.current = false;
      clearInterval(interval);
    };
  }, [fetchMetrics, pollingInterval, enabled]);

  return { metrics, loading, error, refresh: fetchMetrics };
}

// =====================================================================
// 5. Hook : useMLModels (Registre des modèles)
// =====================================================================

export function useMLModels() {
  const [models, setModels] = useState<MLModelInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [reloading, setReloading] = useState<boolean>(false);

  const fetchModels = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getMLModels();
      setModels(res);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la lecture des modèles.');
    } finally {
      setLoading(false);
    }
  }, []);

  const reload = useCallback(async (apiKey?: string) => {
    setReloading(true);
    try {
      await reloadMLModels(apiKey);
      await fetchModels();
    } catch (err: any) {
      throw err;
    } finally {
      setReloading(false);
    }
  }, [fetchModels]);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  return { models, loading, error, reloading, refresh: fetchModels, reload };
}

// =====================================================================
// 6. Hook : useMLAuditLogs (Journal d'audit)
// =====================================================================

export function useMLAuditLogs(params?: AuditQueryParams & { autoRefresh?: boolean; interval?: number }) {
  const { autoRefresh = false, interval = 10000, ...queryParams } = params || {};
  const [logs, setLogs] = useState<MLAuditRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = useCallback(async () => {
    try {
      const res = await getMLAuditLogs(queryParams);
      setLogs(res);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Erreur de chargement de l'audit.");
    } finally {
      setLoading(false);
    }
  }, [queryParams.limit, queryParams.model_name, queryParams.status, queryParams.operation]);

  useEffect(() => {
    fetchLogs();
    if (!autoRefresh) return;

    const timer = setInterval(fetchLogs, interval);
    return () => clearInterval(timer);
  }, [fetchLogs, autoRefresh, interval]);

  return { logs, loading, error, refresh: fetchLogs };
}
