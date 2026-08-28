'use client';

/**
 * components/ml/AnomalyDetectorWidget.tsx — Widget interactif de détection d'anomalies (Isolation Forest).
 */

import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, Activity, AlertTriangle, Loader2, Gauge, CheckCircle2 } from 'lucide-react';
import { useAnomalyDetection } from '@/hooks/use-ml';
import { AnomalySeverity } from '@/lib/ml-api';

interface AnomalyDetectorWidgetProps {
  initialPower?: number;
  initialTemp?: number;
  initialVibration?: number;
  initialPressure?: number;
  machineId?: string;
  onAnomalyDetected?: (severity: AnomalySeverity, isAnomaly: boolean) => void;
}

export function AnomalyDetectorWidget({
  initialPower = 50.0,
  initialTemp = 35.0,
  initialVibration = 3.5,
  initialPressure = 1.5,
  machineId,
  onAnomalyDetected,
}: AnomalyDetectorWidgetProps) {
  const [powerKw, setPowerKw] = useState<number>(initialPower);
  const [temperatureC, setTemperatureC] = useState<number>(initialTemp);
  const [vibrationHz, setVibrationHz] = useState<number>(initialVibration);
  const [pressureBar, setPressureBar] = useState<number>(initialPressure);

  const { data, loading, error, scan } = useAnomalyDetection();

  const handleScan = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    try {
      const now = new Date();
      const res = await scan({
        power_kw: Number(powerKw),
        temperature_c: Number(temperatureC),
        vibration_hz: Number(vibrationHz),
        pressure_bar: Number(pressureBar),
        hour: now.getHours(),
      });
      if (onAnomalyDetected && res) {
        onAnomalyDetected(res.severity, res.is_anomaly);
      }
    } catch (err) {
      console.error("Erreur lors de la détection d'anomalies:", err);
    }
  };

  const getSeverityBadge = (severity: AnomalySeverity) => {
    switch (severity) {
      case 'critique':
        return { bg: 'rgba(220, 38, 38, 0.12)', text: '#dc2626', border: 'rgba(220, 38, 38, 0.3)', label: 'CRITIQUE' };
      case 'modérée':
        return { bg: 'rgba(234, 88, 12, 0.12)', text: '#ea580c', border: 'rgba(234, 88, 12, 0.3)', label: 'MODÉRÉE' };
      case 'faible':
        return { bg: 'rgba(245, 158, 11, 0.12)', text: '#d97706', border: 'rgba(245, 158, 11, 0.3)', label: 'FAIBLE' };
      default:
        return { bg: 'rgba(16, 185, 129, 0.12)', text: '#059669', border: 'rgba(16, 185, 129, 0.3)', label: 'NORMAL' };
    }
  };

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
              background: 'linear-gradient(135deg, rgba(234, 88, 12, 0.15), rgba(220, 38, 38, 0.25))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ea580c',
            }}
          >
            <ShieldAlert size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0, color: 'var(--foreground)' }}>
              Détection d'Anomalies
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-subtle)', margin: 0 }}>
              Algorithme Isolation Forest v2.0.0
            </p>
          </div>
        </div>

        <span
          style={{
            fontSize: '11px',
            fontWeight: 600,
            padding: '3px 8px',
            borderRadius: '6px',
            background: 'rgba(234, 88, 12, 0.08)',
            color: '#ea580c',
            border: '1px solid rgba(234, 88, 12, 0.2)',
          }}
        >
          {machineId ? `Machine: ${machineId}` : 'Capteurs en direct'}
        </span>
      </div>

      {/* Formulaire capteurs */}
      <form onSubmit={handleScan} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px' }}>
            Puissance (kW)
          </label>
          <input
            type="number"
            step="0.1"
            value={powerKw}
            onChange={(e) => setPowerKw(parseFloat(e.target.value) || 0)}
            style={{
              width: '100%',
              padding: '7px 10px',
              borderRadius: '8px',
              border: '1px solid var(--surface-border)',
              background: 'var(--background-alt)',
              fontSize: '13px',
              fontWeight: 600,
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px' }}>
            Température (°C)
          </label>
          <input
            type="number"
            step="0.5"
            value={temperatureC}
            onChange={(e) => setTemperatureC(parseFloat(e.target.value) || 0)}
            style={{
              width: '100%',
              padding: '7px 10px',
              borderRadius: '8px',
              border: '1px solid var(--surface-border)',
              background: 'var(--background-alt)',
              fontSize: '13px',
              fontWeight: 600,
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px' }}>
            Vibrations (Hz)
          </label>
          <input
            type="number"
            step="0.1"
            value={vibrationHz}
            onChange={(e) => setVibrationHz(parseFloat(e.target.value) || 0)}
            style={{
              width: '100%',
              padding: '7px 10px',
              borderRadius: '8px',
              border: '1px solid var(--surface-border)',
              background: 'var(--background-alt)',
              fontSize: '13px',
              fontWeight: 600,
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px' }}>
            Pression (bar)
          </label>
          <input
            type="number"
            step="0.1"
            value={pressureBar}
            onChange={(e) => setPressureBar(parseFloat(e.target.value) || 0)}
            style={{
              width: '100%',
              padding: '7px 10px',
              borderRadius: '8px',
              border: '1px solid var(--surface-border)',
              background: 'var(--background-alt)',
              fontSize: '13px',
              fontWeight: 600,
            }}
          />
        </div>

        {/* Scénarios d'émulation rapides */}
        <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {[
            { label: 'Nominal', p: 45.0, t: 30.0, v: 2.0, pr: 1.2 },
            { label: 'Surchauffe', p: 180.0, t: 88.0, v: 12.0, pr: 2.5 },
            { label: 'Vibration Forte', p: 210.0, t: 72.0, v: 55.0, pr: 4.8 },
          ].map((sc, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setPowerKw(sc.p);
                setTemperatureC(sc.t);
                setVibrationHz(sc.v);
                setPressureBar(sc.pr);
              }}
              style={{
                fontSize: '11px',
                padding: '2px 8px',
                borderRadius: '6px',
                border: '1px solid var(--surface-border)',
                background: 'var(--surface-2)',
                color: 'var(--text-muted)',
                cursor: 'pointer',
              }}
            >
              {sc.label}
            </button>
          ))}
        </div>

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
            background: 'linear-gradient(135deg, #ea580c 0%, #dc2626 100%)',
            borderColor: 'rgba(234, 88, 12, 0.3)',
          }}
        >
          {loading ? (
            <>
              <Loader2 size={16} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
              <span>Analyse sensorielle en cours...</span>
            </>
          ) : (
            <>
              <ShieldAlert size={16} />
              <span>Diagnostiquer avec Isolation Forest</span>
            </>
          )}
        </button>
      </form>

      {/* Erreur */}
      {error && (
        <div
          style={{
            padding: '8px 12px',
            borderRadius: '8px',
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            color: '#dc2626',
            fontSize: '12px',
            marginBottom: '12px',
          }}
        >
          {error}
        </div>
      )}

      {/* Résultat d'anomalie */}
      {data && (
        <div
          style={{
            padding: '14px',
            borderRadius: '12px',
            background: data.is_anomaly
              ? 'linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(234, 88, 12, 0.06))'
              : 'linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(2, 132, 199, 0.06))',
            border: `1px solid ${data.is_anomaly ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {data.is_anomaly ? (
                <ShieldAlert size={22} color="#dc2626" />
              ) : (
                <ShieldCheck size={22} color="#059669" />
              )}
              <div>
                <div style={{ fontSize: '13px', fontWeight: 800, color: data.is_anomaly ? '#dc2626' : '#059669' }}>
                  {data.is_anomaly ? 'ANOMALIE COMPORTEMENTALE DÉTECTÉE' : 'COMPORTEMENT NOMINAL NORMAL'}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-subtle)' }}>
                  Score de décision : <strong>{data.anomaly_score.toFixed(4)}</strong>
                </div>
              </div>
            </div>

            {(() => {
              const badge = getSeverityBadge(data.severity);
              return (
                <span
                  style={{
                    padding: '3px 10px',
                    borderRadius: '20px',
                    fontSize: '11px',
                    fontWeight: 800,
                    background: badge.bg,
                    color: badge.text,
                    border: `1px solid ${badge.border}`,
                  }}
                >
                  {badge.label}
                </span>
              );
            })()}
          </div>

          {/* Barres de probabilité et confiance */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '8px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-muted)', marginBottom: '3px' }}>
                <span>Probabilité d'anomalie</span>
                <strong>{(data.anomaly_probability * 100).toFixed(1)}%</strong>
              </div>
              <div style={{ width: '100%', height: '6px', borderRadius: '3px', background: 'var(--surface-border)', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${data.anomaly_probability * 100}%`,
                    height: '100%',
                    background: data.is_anomaly ? '#dc2626' : '#059669',
                    borderRadius: '3px',
                  }}
                />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-muted)', marginBottom: '3px' }}>
                <span>Indice de Confiance</span>
                <strong>{(data.confidence * 100).toFixed(1)}%</strong>
              </div>
              <div style={{ width: '100%', height: '6px', borderRadius: '3px', background: 'var(--surface-border)', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${data.confidence * 100}%`,
                    height: '100%',
                    background: '#0284c7',
                    borderRadius: '3px',
                  }}
                />
              </div>
            </div>
          </div>

          <div style={{ fontSize: '10px', color: 'var(--text-subtle)', display: 'flex', justifyContent: 'space-between', marginTop: '6px' }}>
            <span>Latence: {data.metadata.execution_time_ms} ms</span>
            <span>ID: {data.request_id.slice(0, 8)}...</span>
          </div>
        </div>
      )}
    </div>
  );
}
