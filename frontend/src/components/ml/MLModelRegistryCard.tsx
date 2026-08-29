'use client';

import React, { useState } from 'react';
import { Database, RefreshCw, Cpu } from 'lucide-react';
import { useMLModels } from '@/hooks/use-ml';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';

export function MLModelRegistryCard() {
  const { models, loading, reloading, reload } = useMLModels();
  const [apiKey, setApiKey] = useState<string>('dev-admin-key');
  const [showKeyInput, setShowKeyInput] = useState<boolean>(false);
  const [toast, setToast] = useState<string | null>(null);

  const handleReload = async () => {
    try {
      await reload(apiKey);
      setToast("Modèles ML rechargés avec succès en mémoire.");
      setTimeout(() => setToast(null), 3500);
    } catch (err: any) {
      setToast(`Échec du rechargement : ${err.message || 'Erreur inconnue'}`);
      setTimeout(() => setToast(null), 4000);
    }
  };

  return (
    <div className="card-standard" style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              backgroundColor: 'var(--bg-surface)',
              color: 'var(--accent-cta)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Database size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
                Registre des Modèles & Artefacts
              </h3>
              <ProvenanceBadge type="synthetique" label="Manifeste v2.0" />
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
              Gestion des versions sérialisées et rechargement à chaud
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setShowKeyInput(!showKeyInput)}
            className="btn-ghost"
            style={{ fontSize: '11px', border: '1px solid var(--border-color)' }}
          >
            {showKeyInput ? 'Masquer Clé' : 'Sécurité Clé'}
          </button>
          <button
            onClick={handleReload}
            disabled={reloading || loading}
            className="btn-cta"
            style={{ minHeight: '36px', padding: '6px 14px', fontSize: '12px' }}
          >
            <RefreshCw size={12} className={reloading ? 'spin-slow' : ''} />
            <span>{reloading ? 'Rechargement...' : 'Recharger Modèles'}</span>
          </button>
        </div>
      </div>

      {showKeyInput && (
        <div style={{ marginBottom: '14px', padding: '12px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-color)' }}>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '4px' }}>
            Clé Administrateur ML (X-API-Key)
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="dev-admin-key"
            className="input-standard"
            style={{ minHeight: '36px', padding: '6px 10px', fontSize: '12px' }}
          />
        </div>
      )}

      {toast && (
        <div
          style={{
            marginBottom: '14px',
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: toast.includes('succès') ? 'var(--status-success-bg)' : 'var(--status-alert-bg)',
            border: `1px solid ${toast.includes('succès') ? 'var(--status-success-border)' : 'var(--status-alert-border)'}`,
            color: toast.includes('succès') ? 'var(--status-success)' : 'var(--status-alert)',
            fontSize: '12px',
            fontWeight: 600,
          }}
        >
          {toast}
        </div>
      )}

      {/* Liste des Modèles du Registre */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {models.map((m, idx) => (
          <div
            key={idx}
            style={{
              padding: '14px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-color)',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Cpu size={16} color="var(--accent-cta)" />
                <span style={{ fontSize: '13px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  {m.name}
                </span>
                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-secondary)',
                    fontFamily: 'IBM Plex Mono, monospace',
                  }}
                >
                  v{m.version}
                </span>
              </div>

              <span
                style={{
                  fontSize: '10px',
                  fontWeight: 800,
                  padding: '2px 8px',
                  borderRadius: '12px',
                  backgroundColor: m.status === 'PROMOTED' || m.status === 'PASS' ? 'var(--status-success-bg)' : 'var(--status-warning-bg)',
                  color: m.status === 'PROMOTED' || m.status === 'PASS' ? 'var(--status-success)' : 'var(--status-warning)',
                  border: `1px solid ${m.status === 'PROMOTED' || m.status === 'PASS' ? 'var(--status-success-border)' : 'var(--status-warning-border)'}`,
                  letterSpacing: '0.04em',
                }}
              >
                {m.status || 'QUALIFIED'}
              </span>
            </div>

            {/* Features requises */}
            {m.features && m.features.length > 0 && (
              <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '2px' }}>
                {m.features.map((feat, fIdx) => (
                  <span
                    key={fIdx}
                    style={{
                      fontSize: '10px',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-muted)',
                      fontFamily: 'IBM Plex Mono, monospace',
                    }}
                  >
                    {feat}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
