'use client';

import React from 'react';

export type UserLevel = 'debutant' | 'amateur' | 'technique';

interface LevelSelectorProps {
  currentLevel: UserLevel;
  onSelectLevel: (level: UserLevel) => void;
  size?: 'sm' | 'md';
  style?: React.CSSProperties;
}

interface LevelOption {
  id: UserLevel;
  label: string;
  badge: string;
  description: string;
}

export const USER_LEVELS: LevelOption[] = [
  {
    id: 'debutant',
    label: 'Débutant',
    badge: 'Ménage',
    description: 'Vue synthétique simplifiée, seuil global et conseils pratiques.',
  },
  {
    id: 'amateur',
    label: 'Amateur',
    badge: 'PME & Commerce',
    description: 'Suivi par équipement, impact sur la marge et rapports hebdomadaires.',
  },
  {
    id: 'technique',
    label: 'Technique',
    badge: 'Industrie & MLOps',
    description: 'Télémétrie complète (kW, °C, Hz, bar), alertes multi-niveaux et Isolation Forest.',
  },
];

/**
 * LevelSelector — Sélecteur de niveau cognitif (Débutant / Amateur / Technique).
 * Modifiable à tout instant pour adapter la densité d'information affichée.
 */
export function LevelSelector({
  currentLevel,
  onSelectLevel,
  size = 'md',
  style = {},
}: LevelSelectorProps) {
  const isSmall = size === 'sm';

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '3px',
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-full)',
        gap: '3px',
        ...style,
      }}
      role="radiogroup"
      aria-label="Sélecteur de niveau d'expertise"
    >
      {USER_LEVELS.map((level) => {
        const isSelected = currentLevel === level.id;
        return (
          <button
            key={level.id}
            type="button"
            role="radio"
            aria-checked={isSelected}
            onClick={() => onSelectLevel(level.id)}
            title={level.description}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: isSmall ? '5px 10px' : '7px 14px',
              fontSize: isSmall ? '11px' : '12px',
              fontWeight: isSelected ? 700 : 500,
              color: isSelected ? '#FFFFFF' : 'var(--text-secondary)',
              backgroundColor: isSelected ? 'var(--accent-cta)' : 'transparent',
              border: 'none',
              borderRadius: 'var(--radius-full)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              whiteSpace: 'nowrap',
            }}
          >
            <span>{level.label}</span>
            {isSelected && (
              <span
                style={{
                  fontSize: '9px',
                  fontWeight: 700,
                  opacity: 0.85,
                  padding: '1px 5px',
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  borderRadius: '10px',
                  letterSpacing: '0.02em',
                }}
              >
                {level.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
