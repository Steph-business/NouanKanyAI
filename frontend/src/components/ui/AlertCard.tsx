'use client';

import React from 'react';
import { AlertOctagon, CheckCircle2, ArrowRight, ShieldAlert, Cpu, History } from 'lucide-react';
import { ProvenanceBadge, ProvenanceType } from './ProvenanceBadge';

export type AlertRegister = 'action_requise' | 'auto_executee';

interface AlertCardProps {
  register: AlertRegister;
  title: string;
  machineId?: string;
  description: string;
  actionText?: string;
  onActionClick?: () => void;
  gainFcfa?: number;
  severity?: 'critique' | 'moderee' | 'faible';
  timestamp?: string;
  provenance?: ProvenanceType;
  loading?: boolean;
  style?: React.CSSProperties;
}

/**
 * AlertCard — Composant d'alerte à 2 registres stricts :
 * 1. Action humaine requise (Urgence, surchauffe, anomalie critique)
 * 2. Action auto-exécutée (Délestage préventif, mode éco journalisé)
 */
export function AlertCard({
  register,
  title,
  machineId,
  description,
  actionText,
  onActionClick,
  gainFcfa,
  severity = 'critique',
  timestamp,
  provenance = 'synthetique',
  loading = false,
  style = {},
}: AlertCardProps) {
  const isActionRequired = register === 'action_requise';

  if (isActionRequired) {
    return (
      <div
        className="alert-action-required animate-fade-in"
        style={{
          boxShadow: '0 4px 20px rgba(214, 41, 62, 0.12)',
          marginBottom: '24px',
          ...style,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                backgroundColor: 'var(--status-alert)',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <AlertOctagon size={20} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--status-alert)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                  ACTION HUMAINE REQUISE
                </span>
                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    backgroundColor: 'rgba(214, 41, 62, 0.15)',
                    color: 'var(--status-alert)',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    textTransform: 'uppercase',
                  }}
                >
                  Sévérité {severity}
                </span>
                <ProvenanceBadge type={provenance} />
              </div>
              <h3 style={{ fontSize: '17px', fontWeight: 800, marginTop: '2px', color: 'var(--text-primary)' }}>
                {title} {machineId && <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>• {machineId}</span>}
              </h3>
            </div>
          </div>

          {timestamp && (
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'IBM Plex Mono, monospace' }}>
              {timestamp}
            </div>
          )}
        </div>

        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '16px' }}>
          {description}
        </p>

        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderTop: '1px solid var(--status-alert-border)',
            paddingTop: '14px',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          {gainFcfa !== undefined && gainFcfa > 0 ? (
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Économies potentielles après intervention :{' '}
              <strong className="tabular-numbers" style={{ color: 'var(--status-success)', fontFamily: 'IBM Plex Mono, monospace' }}>
                +{gainFcfa.toLocaleString('fr-FR')} FCFA
              </strong>
            </div>
          ) : (
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Priorité opérationnelle immédiate
            </div>
          )}

          {actionText && (
            <button
              onClick={onActionClick}
              disabled={loading}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                backgroundColor: 'var(--status-alert)',
                color: '#FFFFFF',
                fontFamily: 'Space Grotesk, sans-serif',
                fontSize: '13px',
                fontWeight: 700,
                borderRadius: 'var(--radius-md)',
                border: 'none',
                cursor: loading ? 'wait' : 'pointer',
                boxShadow: '0 2px 8px rgba(214, 41, 62, 0.25)',
                transition: 'opacity 0.15s ease',
              }}
            >
              <span>{loading ? 'Exécution en cours...' : actionText}</span>
              <ArrowRight size={14} />
            </button>
          )}
        </div>
      </div>
    );
  }

  // Registre 2 : Action auto-exécutée
  return (
    <div
      className="alert-auto-executed animate-fade-in"
      style={{
        marginBottom: '20px',
        ...style,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '28px',
              height: '28px',
              borderRadius: '6px',
              backgroundColor: 'var(--bg-subtle)',
              color: 'var(--status-success)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <CheckCircle2 size={16} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '10px', fontWeight: 800, color: 'var(--text-secondary)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                ACTION AUTO-EXÉCUTÉE & JOURNALISÉE
              </span>
              <ProvenanceBadge type={provenance} />
            </div>
            <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '1px' }}>
              {title} {machineId && <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>({machineId})</span>}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {timestamp && (
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'IBM Plex Mono, monospace' }}>
              {timestamp}
            </div>
          )}
          {actionText && (
            <button
              onClick={onActionClick}
              className="btn-ghost"
              style={{ padding: '4px 8px', fontSize: '11px' }}
            >
              {actionText}
            </button>
          )}
        </div>
      </div>

      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px', lineHeight: 1.4 }}>
        {description}
      </div>
    </div>
  );
}
