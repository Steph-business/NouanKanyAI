'use client';

import React from 'react';
import { CheckCircle2, AlertTriangle, AlertOctagon, RefreshCw } from 'lucide-react';
import { useMLHealth } from '@/hooks/use-ml';

interface MLHealthBadgeProps {
  showDetails?: boolean;
  onRefreshClick?: () => void;
  style?: React.CSSProperties;
}

export function MLHealthBadge({ showDetails = false, style = {} }: MLHealthBadgeProps) {
  const { health, loading, refresh } = useMLHealth({ pollingInterval: 8000 });

  if (loading && !health) {
    return (
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: 'var(--radius-full)',
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-color)',
          fontSize: '11px',
          color: 'var(--text-secondary)',
          ...style,
        }}
      >
        <RefreshCw size={11} className="spin-slow" />
        <span>Vérification IA...</span>
      </div>
    );
  }

  const status = health?.status || 'unhealthy';
  const isHealthy = status === 'healthy';
  const isDegraded = status === 'degraded';

  const config = isHealthy
    ? {
        bg: 'var(--status-success-bg)',
        border: 'var(--status-success-border)',
        text: 'var(--status-success)',
        icon: CheckCircle2,
        label: 'IA Opérationnelle',
      }
    : isDegraded
    ? {
        bg: 'var(--status-warning-bg)',
        border: 'var(--status-warning-border)',
        text: 'var(--status-warning)',
        icon: AlertTriangle,
        label: 'IA Dégradée',
      }
    : {
        bg: 'var(--status-alert-bg)',
        border: 'var(--status-alert-border)',
        text: 'var(--status-alert)',
        icon: AlertOctagon,
        label: 'IA Indisponible',
      };

  const Icon = config.icon;
  const durationMs = health?.details?.check_duration_ms;

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '5px 12px',
        borderRadius: 'var(--radius-full)',
        backgroundColor: config.bg,
        border: `1px solid ${config.border}`,
        fontSize: '11px',
        fontWeight: 700,
        color: config.text,
        cursor: 'pointer',
        transition: 'all 0.15s ease',
        userSelect: 'none',
        ...style,
      }}
      title={`Modèles: ${health?.models_loaded ? 'Chargés' : 'Absents'} | Registre: ${health?.registry_loaded ? 'OK' : 'Non'} | v${health?.version || '2.0.0'}`}
      onClick={() => refresh()}
    >
      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: config.text,
          boxShadow: `0 0 5px ${config.text}`,
        }}
      />
      <Icon size={12} strokeWidth={2.5} />
      <span>{config.label}</span>

      {showDetails && (
        <span
          className="tabular-numbers"
          style={{
            fontSize: '10px',
            opacity: 0.85,
            paddingLeft: '6px',
            borderLeft: `1px solid ${config.border}`,
            fontFamily: 'IBM Plex Mono, monospace',
          }}
        >
          v{health?.version || '2.0'} {durationMs ? `(${durationMs.toFixed(1)}ms)` : ''}
        </span>
      )}
    </div>
  );
}
