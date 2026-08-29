'use client';

import React, { useState } from 'react';
import { TrendingUp, Clock, Cpu, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { usePrediction } from '@/hooks/use-ml';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';

interface ForecastingWidgetProps {
  initialPower?: number;
  initialTemp?: number;
  machineId?: string;
  onPredictionComplete?: (kw: number) => void;
  style?: React.CSSProperties;
}

export function ForecastingWidget({
  initialPower = 65.0,
  initialTemp = 30.0,
  machineId,
  onPredictionComplete,
  style = {},
}: ForecastingWidgetProps) {
  const [powerKw, setPowerKw] = useState<number>(initialPower);
  const [temperatureC, setTemperatureC] = useState<number>(initialTemp);
  const [isPeakHour, setIsPeakHour] = useState<boolean>(true);

  const { data, loading, error, predict } = usePrediction();

  const handleRunForecast = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    try {
      const now = new Date();
      const res = await predict({
        power_kw: Number(powerKw),
        temperature_c: Number(temperatureC),
        hour: now.getHours(),
        day_of_week: (now.getDay() + 6) % 7,
        is_weekend: [0, 6].includes(now.getDay()) ? 1 : 0,
        is_peak_hour: isPeakHour ? 1 : 0,
      });
      if (onPredictionComplete && res?.prediction) {
        onPredictionComplete(res.prediction);
      }
    } catch (err) {
      console.error("Erreur lors de la prévision:", err);
    }
  };

  const predictedKw = data?.prediction ?? null;
  const estimatedCostFcfa = predictedKw !== null ? Math.round(predictedKw * 68) : null;
  const deltaPower = predictedKw !== null ? predictedKw - powerKw : null;

  return (
    <div className="card-standard" style={{ padding: '24px', backgroundColor: 'var(--bg-card)', ...style }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '18px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              backgroundColor: 'var(--status-success-bg)',
              color: 'var(--status-success)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <TrendingUp size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
                Prévision Énergétique t+1h
              </h3>
              <ProvenanceBadge type="synthetique" label="XGBoost v2.0" />
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
              Dataset d'entraînement synthétique • Inférence multi-lag
            </p>
          </div>
        </div>

        {machineId && (
          <span style={{ fontSize: '11px', fontWeight: 700, padding: '3px 8px', borderRadius: '4px', backgroundColor: 'var(--bg-surface)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
            Machine : {machineId}
          </span>
        )}
      </div>

      {/* Formulaire de saisie interactive */}
      <form onSubmit={handleRunForecast} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '18px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
            Puissance actuelle (kW)
          </label>
          <input
            type="number"
            step="0.1"
            min="0"
            max="3000"
            value={powerKw}
            onChange={(e) => setPowerKw(parseFloat(e.target.value) || 0)}
            className="input-standard tabular-numbers"
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
            Température ambiante (°C)
          </label>
          <input
            type="number"
            step="0.5"
            min="-20"
            max="120"
            value={temperatureC}
            onChange={(e) => setTemperatureC(parseFloat(e.target.value) || 0)}
            className="input-standard tabular-numbers"
          />
        </div>

        {/* Presets rapides */}
        <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {[
            { label: 'Standard (45 kW)', p: 45.0, t: 28.0 },
            { label: 'Industriel (120 kW)', p: 120.0, t: 34.0 },
            { label: 'Haute Charge (280 kW)', p: 280.0, t: 42.0 },
          ].map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setPowerKw(preset.p);
                setTemperatureC(preset.t);
              }}
              className="btn-ghost"
              style={{
                fontSize: '11px',
                padding: '4px 8px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
                backgroundColor: 'var(--bg-surface)',
              }}
            >
              {preset.label}
            </button>
          ))}
        </div>

        {/* Bouton d'inférence */}
        <button
          type="submit"
          disabled={loading}
          className="btn-cta"
          style={{ gridColumn: '1 / -1' }}
        >
          {loading ? (
            <>
              <Loader2 size={16} className="spin-slow" />
              <span>Calcul d'inférence XGBoost en cours...</span>
            </>
          ) : (
            <>
              <Sparkles size={16} />
              <span>Calculer la prévision énergétique</span>
            </>
          )}
        </button>
      </form>

      {/* Message d'erreur éventuel */}
      {error && (
        <div
          style={{
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--status-alert-bg)',
            border: '1px solid var(--status-alert-border)',
            color: 'var(--status-alert)',
            fontSize: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '16px',
          }}
        >
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Résultat d'inférence */}
      {data && (
        <div
          className="animate-fade-in"
          style={{
            padding: '16px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-color)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Charge Prévue à t+1h
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                <span
                  className="tabular-numbers"
                  style={{
                    fontSize: '28px',
                    fontWeight: 800,
                    color: 'var(--text-primary)',
                    fontFamily: 'IBM Plex Mono, monospace',
                  }}
                >
                  {data.prediction.toFixed(2)}
                </span>
                <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-secondary)' }}>
                  {data.unit}
                </span>
                {deltaPower !== null && (
                  <span
                    className="tabular-numbers"
                    style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      color: deltaPower >= 0 ? 'var(--accent-cost)' : 'var(--status-success)',
                      marginLeft: '4px',
                    }}
                  >
                    ({deltaPower >= 0 ? '+' : ''}{deltaPower.toFixed(1)} kW)
                  </span>
                )}
              </div>
            </div>

            {estimatedCostFcfa !== null && (
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>Coût estimé CIE</div>
                <div className="tabular-numbers" style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'IBM Plex Mono, monospace' }}>
                  ~{estimatedCostFcfa.toLocaleString('fr-FR')} FCFA / h
                </div>
              </div>
            )}
          </div>

          {/* Métadonnées de l'inférence */}
          <div
            style={{
              display: 'flex',
              gap: '12px',
              flexWrap: 'wrap',
              fontSize: '11px',
              color: 'var(--text-muted)',
              borderTop: '1px solid var(--border-subtle)',
              paddingTop: '8px',
              marginTop: '8px',
            }}
          >
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={12} />
              Latence : <strong className="tabular-numbers">{data.metadata.execution_time_ms} ms</strong>
            </span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Cpu size={12} />
              {data.model_name} (v{data.model_version})
            </span>
            <span title={`UUID: ${data.request_id}`} style={{ cursor: 'help', fontFamily: 'IBM Plex Mono, monospace' }}>
              ID: {data.request_id.slice(0, 8)}...
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
