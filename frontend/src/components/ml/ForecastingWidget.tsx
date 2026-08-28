'use client';

/**
 * components/ml/ForecastingWidget.tsx — Widget interactif de prévision de consommation énergétique (XGBoost).
 */

import React, { useState } from 'react';
import { Zap, TrendingUp, Clock, Cpu, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { usePrediction } from '@/hooks/use-ml';

interface ForecastingWidgetProps {
  initialPower?: number;
  initialTemp?: number;
  machineId?: string;
  onPredictionComplete?: (kw: number) => void;
}

export function ForecastingWidget({
  initialPower = 65.0,
  initialTemp = 30.0,
  machineId,
  onPredictionComplete,
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

  // Calcul du coût estimé t+1h en Francs CFA (Tarif moyen CIE ~68 FCFA/kWh)
  const predictedKw = data?.prediction ?? null;
  const estimatedCostFcfa = predictedKw !== null ? Math.round(predictedKw * 68) : null;
  const deltaPower = predictedKw !== null ? predictedKw - powerKw : null;

  return (
    <div className="glass-card" style={{ padding: '24px', position: 'relative' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.25))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#059669',
            }}
          >
            <TrendingUp size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0, color: 'var(--foreground)' }}>
              Prévision Énergétique t+1h
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-subtle)', margin: 0 }}>
              Modèle prédictif XGBoost v2.0.0
            </p>
          </div>
        </div>

        <span
          style={{
            fontSize: '11px',
            fontWeight: 600,
            padding: '3px 8px',
            borderRadius: '6px',
            background: 'rgba(2, 132, 199, 0.08)',
            color: '#0284c7',
            border: '1px solid rgba(2, 132, 199, 0.2)',
          }}
        >
          {machineId ? `Machine: ${machineId}` : 'Multi-sources'}
        </span>
      </div>

      {/* Formulaire de saisie interactive */}
      <form onSubmit={handleRunForecast} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '18px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
            Puissance actuelle (kW)
          </label>
          <input
            type="number"
            step="0.1"
            min="0"
            max="3000"
            value={powerKw}
            onChange={(e) => setPowerKw(parseFloat(e.target.value) || 0)}
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid var(--surface-border)',
              background: 'var(--background-alt)',
              fontSize: '14px',
              fontWeight: 600,
              color: 'var(--foreground)',
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
            Température ambiante (°C)
          </label>
          <input
            type="number"
            step="0.5"
            min="-20"
            max="120"
            value={temperatureC}
            onChange={(e) => setTemperatureC(parseFloat(e.target.value) || 0)}
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid var(--surface-border)',
              background: 'var(--background-alt)',
              fontSize: '14px',
              fontWeight: 600,
              color: 'var(--foreground)',
            }}
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
              style={{
                fontSize: '11px',
                padding: '3px 8px',
                borderRadius: '6px',
                border: '1px solid var(--surface-border)',
                background: 'var(--surface-2)',
                color: 'var(--text-muted)',
                cursor: 'pointer',
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
          className="btn-primary"
          style={{
            gridColumn: '1 / -1',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '10px 16px',
            fontSize: '13px',
          }}
        >
          {loading ? (
            <>
              <Loader2 size={16} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
              <span>Calcul d'inférence en cours...</span>
            </>
          ) : (
            <>
              <Sparkles size={16} />
              <span>Calculer la prévision XGBoost</span>
            </>
          )}
        </button>
      </form>

      {/* Message d'erreur éventuel */}
      {error && (
        <div
          style={{
            padding: '10px 14px',
            borderRadius: '8px',
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            color: '#dc2626',
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
          style={{
            padding: '16px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.06), rgba(2, 132, 199, 0.06))',
            border: '1px solid rgba(16, 185, 129, 0.2)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
            <div>
              <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Charge Prévue (t+1h)
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                <span style={{ fontSize: '28px', fontWeight: 800, color: '#059669', fontFamily: 'Outfit, sans-serif' }}>
                  {data.prediction.toFixed(2)}
                </span>
                <span style={{ fontSize: '14px', fontWeight: 700, color: '#059669' }}>
                  {data.unit}
                </span>
                {deltaPower !== null && (
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      color: deltaPower >= 0 ? '#ea580c' : '#059669',
                      marginLeft: '4px',
                    }}
                  >
                    ({deltaPower >= 0 ? '+' : ''}{deltaPower.toFixed(1)} kW vs actuelle)
                  </span>
                )}
              </div>
            </div>

            {estimatedCostFcfa !== null && (
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '10px', color: 'var(--text-subtle)' }}>Coût estimé / heure</div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--foreground)' }}>
                  ~{estimatedCostFcfa.toLocaleString('fr-FR')} FCFA
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
              fontSize: '10px',
              color: 'var(--text-subtle)',
              borderTop: '1px solid rgba(16, 185, 129, 0.15)',
              paddingTop: '8px',
              marginTop: '8px',
            }}
          >
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={12} />
              Latence : <strong>{data.metadata.execution_time_ms} ms</strong>
            </span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Cpu size={12} />
              {data.model_name} (v{data.model_version})
            </span>
            <span title={`UUID: ${data.request_id}`} style={{ cursor: 'help' }}>
              ID: {data.request_id.slice(0, 8)}...
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
