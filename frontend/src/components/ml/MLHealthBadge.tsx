'use client';

/**
 * components/ml/MLHealthBadge.tsx — Badge d'état opérationnel et de santé de la couche ML.
 */

import React from 'react';
import { Activity, CheckCircle2, AlertTriangle, XCircle, RefreshCw } from 'lucide-react';
import { useMLHealth } from '@/hooks/use-ml';

interface MLHealthBadgeProps {
  showDetails?: boolean;
  onRefreshClick?: () => void;
}

export function MLHealthBadge({ showDetails = false }: MLHealthBadgeProps) {
  const { health, loading, refresh } = useMLHealth({ pollingInterval: 8000 });

  if (loading && !health) {
    return (
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 10px', borderRadius: '20px', background: 'rgba(2, 132, 199, 0.08)', border: '1px solid rgba(2, 132, 199, 0.2)', fontSize: '12px', color: '#0284c7' }}>
        <RefreshCw size={12} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
        <span>Vérification IA...</span>
      </div>
    );
  }

  const status = health?.status || 'unhealthy';
  const isHealthy = status === 'healthy';
  const isDegraded = status === 'degraded';

  const config = isHealthy
    ? {
        bg: 'rgba(16, 185, 129, 0.1)',
        border: 'rgba(16, 185, 129, 0.25)',
        text: '#059669',
        icon: CheckCircle2,
        label: 'IA Opérationnelle',
      }
    : isDegraded
    ? {
        bg: 'rgba(245, 158, 11, 0.1)',
        border: 'rgba(245, 158, 11, 0.25)',
        text: '#d97706',
        icon: AlertTriangle,
        label: 'IA Dégradée',
      }
    : {
        bg: 'rgba(239, 68, 68, 0.1)',
        border: 'rgba(239, 68, 68, 0.25)',
        text: '#dc2626',
        icon: XCircle,
        label: 'IA Indisponible',
      };

  const Icon = config.icon;
  const durationMs = health?.details?.check_duration_ms;

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '8px',
        padding: '5px 12px',
        borderRadius: '9999px',
        background: config.bg,
        border: `1px solid ${config.border}`,
        fontSize: '12px',
        fontWeight: 600,
        color: config.text,
        cursor: 'pointer',
        transition: 'all 0.2s ease',
      }}
      title={`Modèles: ${health?.models_loaded ? 'Chargés' : 'Absents'} | Registre: ${health?.registry_loaded ? 'OK' : 'Non'} | v${health?.version || '2.0.0'}`}
      onClick={() => refresh()}
    >
      <span style={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
        <span
          style={{
            width: '7px',
            height: '7px',
            borderRadius: '50%',
            backgroundColor: config.text,
            marginRight: '6px',
            boxShadow: `0 0 6px ${config.text}`,
          }}
        />
        <Icon size={14} style={{ marginRight: '4px' }} />
        <span>{config.label}</span>
      </span>

      {showDetails && (
        <span style={{ fontSize: '10px', opacity: 0.85, paddingLeft: '4px', borderLeft: `1px solid ${config.border}` }}>
          v{health?.version || '2.0'} {durationMs ? `(${durationMs.toFixed(1)}ms)` : ''}
        </span>
      )}
    </div>
  );
}
