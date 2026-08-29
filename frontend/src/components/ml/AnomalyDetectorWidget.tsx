'use client';

import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, Loader2 } from 'lucide-react';
import { useAnomalyDetection } from '@/hooks/use-ml';
import { AnomalySeverity } from '@/lib/ml-api';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';

interface AnomalyDetectorWidgetProps {
  initialPower?: number;
  initialTemp?: number;
  initialVibration?: number;
  initialPressure?: number;
  machineId?: string;
  onAnomalyDetected?: (severity: AnomalySeverity, isAnomaly: boolean) => void;
  style?: React.CSSProperties;
}

export function AnomalyDetectorWidget({
  initialPower = 50.0,
  initialTemp = 35.0,
  initialVibration = 3.5,
  initialPressure = 1.5,
  machineId,
  onAnomalyDetected,
  style = {},
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
        return { bg: 'var(--status-alert-bg)', text: 'var(--status-alert)', border: 'var(--status-alert-border)', label: 'CRITIQUE' };
      case 'modérée':
        return { bg: 'var(--status-warning-bg)', text: 'var(--status-warning)', border: 'var(--status-warning-border)', label: 'MODÉRÉE' };
      case 'faible':
        return { bg: 'var(--status-warning-bg)', text: 'var(--status-warning)', border: 'var(--status-warning-border)', label: 'FAIBLE' };
      default:
        return { bg: 'var(--status-success-bg)', text: 'var(--status-success)', border: 'var(--status-success-border)', label: 'NORMAL' };
    }
  };

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
              backgroundColor: 'var(--status-warning-bg)',
              color: 'var(--status-warning)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <ShieldAlert size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
                Détection d'Anomalies
              </h3>
              <ProvenanceBadge type="synthetique" label="Isolation Forest v2.0" />
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
              Classification multi-paramétrique (puissance, thermique, vibration, pression)
            </p>
          </div>
        </div>

        {machineId && (
          <span style={{ fontSize: '11px', fontWeight: 700, padding: '3px 8px', borderRadius: '4px', backgroundColor: 'var(--bg-surface)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
            Machine : {machineId}
          </span>
        )}
      </div>

      {/* Formulaire capteurs */}
      <form onSubmit={handleScan} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '4px' }}>
            Puissance (kW)
          </label>
          <input
            type="number"
            step="0.1"
            value={powerKw}
            onChange={(e) => setPowerKw(parseFloat(e.target.value) || 0)}
            className="input-standard tabular-numbers"
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '4px' }}>
            Température (°C)
          </label>
          <input
            type="number"
            step="0.5"
            value={temperatureC}
            onChange={(e) => setTemperatureC(parseFloat(e.target.value) || 0)}
            className="input-standard tabular-numbers"
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '4px' }}>
            Vibrations (Hz)
          </label>
          <input
            type="number"
            step="0.1"
            value={vibrationHz}
            onChange={(e) => setVibrationHz(parseFloat(e.target.value) || 0)}
            className="input-standard tabular-numbers"
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '4px' }}>
            Pression (bar)
          </label>
          <input
            type="number"
            step="0.1"
            value={pressureBar}
            onChange={(e) => setPressureBar(parseFloat(e.target.value) || 0)}
            className="input-standard tabular-numbers"
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
              className="btn-ghost"
              style={{
                fontSize: '11px',
                padding: '3px 8px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
                backgroundColor: 'var(--bg-surface)',
              }}
            >
              {sc.label}
            </button>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-cta"
          style={{ gridColumn: '1 / -1' }}
        >
          {loading ? (
            <>
              <Loader2 size={16} className="spin-slow" />
              <span>Diagnostic Isolation Forest en cours...</span>
            </>
          ) : (
            <>
              <ShieldAlert size={16} />
              <span>Diagnostiquer les anomalies</span>
            </>
          )}
        </button>
      </form>

      {/* Erreur */}
      {error && (
        <div
          style={{
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--status-alert-bg)',
            border: '1px solid var(--status-alert-border)',
            color: 'var(--status-alert)',
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
          className="animate-fade-in"
          style={{
            padding: '16px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--bg-surface)',
            border: `1px solid ${data.is_anomaly ? 'var(--status-alert-border)' : 'var(--status-success-border)'}`,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {data.is_anomaly ? (
                <ShieldAlert size={22} color="var(--status-alert)" />
              ) : (
                <ShieldCheck size={22} color="var(--status-success)" />
              )}
              <div>
                <div style={{ fontSize: '13px', fontWeight: 800, color: data.is_anomaly ? 'var(--status-alert)' : 'var(--status-success)' }}>
                  {data.is_anomaly ? 'ANOMALIE COMPORTEMENTALE DÉTECTÉE' : 'COMPORTEMENT NOMINAL NORMAL'}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                  Score de décision : <strong className="tabular-numbers">{data.anomaly_score.toFixed(4)}</strong>
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
                    backgroundColor: badge.bg,
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
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '8px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                <span>Probabilité d'anomalie</span>
                <strong className="tabular-numbers">{(data.anomaly_probability * 100).toFixed(1)}%</strong>
              </div>
              <div style={{ width: '100%', height: '6px', borderRadius: '3px', backgroundColor: 'var(--border-color)', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${data.anomaly_probability * 100}%`,
                    height: '100%',
                    backgroundColor: data.is_anomaly ? 'var(--status-alert)' : 'var(--status-success)',
                    borderRadius: '3px',
                  }}
                />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                <span>Indice de Confiance</span>
                <strong className="tabular-numbers">{(data.confidence * 100).toFixed(1)}%</strong>
              </div>
              <div style={{ width: '100%', height: '6px', borderRadius: '3px', backgroundColor: 'var(--border-color)', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${data.confidence * 100}%`,
                    height: '100%',
                    backgroundColor: 'var(--cie-domestique)',
                    borderRadius: '3px',
                  }}
                />
              </div>
            </div>
          </div>

          <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between', marginTop: '8px', borderTop: '1px solid var(--border-subtle)', paddingTop: '6px' }}>
            <span>Latence : <strong className="tabular-numbers">{data.metadata.execution_time_ms} ms</strong></span>
            <span style={{ fontFamily: 'IBM Plex Mono, monospace' }}>ID : {data.request_id.slice(0, 8)}...</span>
          </div>
        </div>
      )}
    </div>
  );
}
