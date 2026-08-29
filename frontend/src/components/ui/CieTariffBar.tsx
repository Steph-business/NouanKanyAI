'use client';

import React, { useState } from 'react';
import { ProvenanceBadge } from './ProvenanceBadge';

interface CieTariffBarProps {
  currentKwh?: number;
  showDetails?: boolean;
  interactive?: boolean;
  onTierSelect?: (tierKey: string) => void;
  style?: React.CSSProperties;
}

interface Tier {
  id: string;
  name: string;
  range: string;
  rate: number;
  unit: string;
  color: string;
  bgColor: string;
  percent: number;
  description: string;
}

export const CIE_TIERS: Tier[] = [
  {
    id: 'sociale',
    name: 'Sociale',
    range: '0 – 80 kWh',
    rate: 36,
    unit: 'FCFA / kWh',
    color: '#1B7A43',
    bgColor: '#E8F5ED',
    percent: 16,
    description: 'Usage domestique modéré subventionné',
  },
  {
    id: 'domestique',
    name: 'Domestique',
    range: '81 – 150 kWh',
    rate: 46,
    unit: 'FCFA / kWh',
    color: '#2B6CB0',
    bgColor: '#EBF8FF',
    percent: 14,
    description: 'Ménages avec équipements de confort standards',
  },
  {
    id: 'non_domestique',
    name: 'Non Domestique',
    range: '151 – 500 kWh',
    rate: 68,
    unit: 'FCFA / kWh',
    color: '#D67A00',
    bgColor: '#FEF3C7',
    percent: 35,
    description: 'PME, commerces, ateliers et climatisation continue',
  },
  {
    id: 'industriel',
    name: 'Professionnelle / Industrie',
    range: '> 500 kWh',
    rate: 96,
    unit: 'FCFA / kWh',
    color: '#C53030',
    bgColor: '#FEE2E2',
    percent: 35,
    description: 'Grandes installations industrielles et fortes puissances',
  },
];

/**
 * CieTariffBar — Barre de paliers tarifaires officielle CIE (Côte d'Ivoire).
 * Élément récurrent de la signature visuelle du produit.
 */
export function CieTariffBar({
  currentKwh,
  showDetails = true,
  interactive = true,
  onTierSelect,
  style = {},
}: CieTariffBarProps) {
  const [activeTier, setActiveTier] = useState<Tier | null>(null);

  const getTierForKwh = (kwh: number): Tier => {
    if (kwh <= 80) return CIE_TIERS[0];
    if (kwh <= 150) return CIE_TIERS[1];
    if (kwh <= 500) return CIE_TIERS[2];
    return CIE_TIERS[3];
  };

  const currentTier = currentKwh !== undefined ? getTierForKwh(currentKwh) : null;
  const displayedTier = activeTier || currentTier || CIE_TIERS[2];

  return (
    <div
      className="card-standard"
      style={{
        padding: '20px',
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-color)',
        ...style,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: 800, letterSpacing: '0.08em', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
            Grille Tarifaire Officielle CIE
          </span>
          <ProvenanceBadge type="mesure" label="Réglementaire" />
        </div>

        {currentKwh !== undefined && (
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Palier détecté : <strong style={{ color: currentTier?.color }}>{currentTier?.name}</strong> (
            <span className="tabular-numbers">{currentKwh.toFixed(1)} kWh</span>)
          </div>
        )}
      </div>

      {/* Barre segmentée continue */}
      <div
        style={{
          display: 'flex',
          height: '14px',
          width: '100%',
          borderRadius: '7px',
          overflow: 'hidden',
          backgroundColor: 'var(--border-color)',
          gap: '2px',
          marginBottom: '16px',
        }}
      >
        {CIE_TIERS.map((tier) => {
          const isSelected = displayedTier.id === tier.id;
          return (
            <div
              key={tier.id}
              onClick={() => {
                if (interactive) {
                  setActiveTier(tier);
                  if (onTierSelect) onTierSelect(tier.id);
                }
              }}
              style={{
                flex: tier.percent,
                backgroundColor: tier.color,
                opacity: isSelected ? 1 : 0.65,
                cursor: interactive ? 'pointer' : 'default',
                transition: 'opacity 0.2s ease, transform 0.2s ease',
                position: 'relative',
              }}
              title={`${tier.name} (${tier.range}) : ${tier.rate} FCFA/kWh`}
            />
          );
        })}
      </div>

      {/* Grille des 4 Paliers */}
      {showDetails && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
            gap: '10px',
          }}
        >
          {CIE_TIERS.map((tier) => {
            const isSelected = displayedTier.id === tier.id;
            return (
              <div
                key={tier.id}
                onClick={() => {
                  if (interactive) {
                    setActiveTier(tier);
                    if (onTierSelect) onTierSelect(tier.id);
                  }
                }}
                style={{
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-sm)',
                  border: `1px solid ${isSelected ? tier.color : 'var(--border-color)'}`,
                  backgroundColor: isSelected ? 'var(--bg-card)' : 'transparent',
                  cursor: interactive ? 'pointer' : 'default',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                  <span
                    style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: tier.color,
                      flexShrink: 0,
                    }}
                  />
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {tier.name}
                  </span>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  {tier.range}
                </div>
                <div
                  className="tabular-numbers"
                  style={{
                    fontSize: '15px',
                    fontWeight: 700,
                    color: tier.color,
                    fontFamily: 'IBM Plex Mono, monospace',
                  }}
                >
                  {tier.rate} <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>FCFA</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
