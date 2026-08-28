'use client';

/**
 * components/ml/MLModelRegistryCard.tsx — Affichage du registre de modèles avec rechargement à chaud.
 */

import React, { useState } from 'react';
import { Database, RefreshCw, Cpu, Layers, CheckCircle, Tag, Shield } from 'lucide-react';
import { useMLModels } from '@/hooks/use-ml';

export function MLModelRegistryCard() {
  const { models, loading, reloading, reload, refresh } = useMLModels();
  const [apiKey, setApiKey] = useState<string>('dev-admin-key');
  const [showKeyInput, setShowKeyInput] = useState<boolean>(false);
  const [toast, setToast] = useState<string | null>(null);

  const handleReload = async () => {
    try {
      await reload(apiKey);
      setToast("Modèles ML rechargés avec succès en mémoire !");
      setTimeout(() => setToast(null), 3500);
    } catch (err: any) {
      setToast(`Échec du rechargement : ${err.message || 'Erreur inconnue'}`);
      setTimeout(() => setToast(null), 4000);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, rgba(2, 132, 199, 0.15), rgba(5, 150, 105, 0.25))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#0284c7',
            }}
          >
            <Database size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0, color: 'var(--foreground)' }}>
              Registre des Modèles & Artefacts
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-subtle)', margin: 0 }}>
              Gestion des versions et rechargement à chaud
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setShowKeyInput(!showKeyInput)}
            style={{
              padding: '6px 10px',
              borderRadius: '6px',
              border: '1px solid var(--surface-border)',
              background: 'var(--surface-2)',
              fontSize: '11px',
              fontWeight: 600,
              color: 'var(--text-muted)',
              cursor: 'pointer',
            }}
          >
            {showKeyInput ? 'Masquer Clé' : 'Sécurité Clé'}
          </button>
          <button
            onClick={handleReload}
            disabled={reloading || loading}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: '6px',
              border: '1px solid rgba(5, 150, 105, 0.3)',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: '#fff',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={12} className={reloading ? 'spin' : ''} style={{ animation: reloading ? 'spin 1s linear infinite' : 'none' }} />
            <span>{reloading ? 'Rechargement...' : 'Recharger Modèles'}</span>
          </button>
        </div>
      </div>

      {showKeyInput && (
        <div style={{ marginBottom: '14px', padding: '10px 14px', borderRadius: '8px', background: 'var(--surface-2)', border: '1px solid var(--surface-border)' }}>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px' }}>
            Clé Administrateur ML (X-API-Key)
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="dev-admin-key"
            style={{
              width: '100%',
              padding: '6px 10px',
              borderRadius: '6px',
              border: '1px solid var(--surface-border)',
              background: 'var(--background-alt)',
              fontSize: '12px',
              color: 'var(--foreground)',
            }}
          />
        </div>
      )}

      {toast && (
        <div
          style={{
            marginBottom: '14px',
            padding: '8px 12px',
            borderRadius: '8px',
            background: toast.includes('succès') ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            border: `1px solid ${toast.includes('succès') ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            color: toast.includes('succès') ? '#059669' : '#dc2626',
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
              borderRadius: '10px',
              background: 'var(--surface-2)',
              border: '1px solid var(--surface-border)',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Cpu size={16} color="#059669" />
                <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--foreground)' }}>
                  {m.name}
                </span>
                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    background: 'rgba(5, 150, 105, 0.1)',
                    color: '#059669',
                  }}
                >
                  v{m.version}
                </span>
              </div>

              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  padding: '3px 8px',
                  borderRadius: '6px',
                  background: m.status === 'PROMOTED' || m.status === 'PASS' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(245, 158, 11, 0.12)',
                  color: m.status === 'PROMOTED' || m.status === 'PASS' ? '#059669' : '#d97706',
                  border: `1px solid ${m.status === 'PROMOTED' || m.status === 'PASS' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
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
                      background: 'var(--surface)',
                      border: '1px solid var(--surface-border)',
                      color: 'var(--text-subtle)',
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
