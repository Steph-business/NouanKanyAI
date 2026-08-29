'use client';

import React from 'react';
import { CheckCircle2, Calculator, Cpu } from 'lucide-react';

export type ProvenanceType = 'mesure' | 'estime' | 'synthetique';

interface ProvenanceBadgeProps {
  type: ProvenanceType;
  label?: string;
  showIcon?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * ProvenanceBadge — Signature visuelle d'honnêteté produit.
 * "Une donnée est mesurée, estimée, ou synthétique, jamais inventée."
 */
export function ProvenanceBadge({
  type,
  label,
  showIcon = true,
  className = '',
  style = {},
}: ProvenanceBadgeProps) {
  const configs = {
    mesure: {
      defaultLabel: 'Mesuré',
      className: 'badge-mesure',
      icon: CheckCircle2,
      title: 'Donnée physique relevée ou mesurée',
    },
    estime: {
      defaultLabel: 'Estimé',
      className: 'badge-estime',
      icon: Calculator,
      title: 'Donnée calculée par extrapolation ou formule tarifaire',
    },
    synthetique: {
      defaultLabel: 'Synthétique',
      className: 'badge-synthetique',
      icon: Cpu,
      title: 'Donnée simulée issue de modèles ML (XGBoost/Isolation Forest)',
    },
  };

  const config = configs[type] || configs.synthetique;
  const Icon = config.icon;
  const displayLabel = label || config.defaultLabel;

  return (
    <span
      className={`${config.className} ${className}`}
      title={config.title}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        verticalAlign: 'middle',
        userSelect: 'none',
        ...style,
      }}
    >
      {showIcon && <Icon size={11} strokeWidth={2.5} />}
      <span>{displayLabel}</span>
    </span>
  );
}
