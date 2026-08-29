'use client';

import React, { useState, useEffect } from 'react';
import {
  Settings,
  Database,
  Users,
  Activity,
  Cpu,
  ShieldCheck,
  Server,
  RefreshCw,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';
import { API_URL } from '@/lib/api';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';
import { MLMetricsDashboard, MLModelRegistryCard, MLAuditTable } from '@/components/ml';
import { Toast, ToastMessage } from '@/components/ui/Toast';

export default function AdminPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Toast
  const [toast, setToast] = useState<ToastMessage | null>(null);

  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    setToast({ id: Date.now().toString(), message, type });
  };

  const fetchAdminMetrics = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/metrics`);
      const json = await res.json();
      setMetrics(json);
    } catch (err) {
      console.error("Erreur métriques admin:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminMetrics();
  }, []);

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cta)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Administration & Observabilité Système
            </span>
            <ProvenanceBadge type="synthetique" label="Dataset Synthétique" />
          </div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
            Console Administrateur MLOps
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
            Supervision des instances de serveurs, des pipelines d'entraînement et des modèles IA.
          </p>
        </div>

        <button
          onClick={() => {
            fetchAdminMetrics();
            showToast("Métriques système réactualisées.", 'info');
          }}
          className="btn-outline"
          style={{ fontSize: '12px', padding: '8px 14px' }}
        >
          <RefreshCw size={14} />
          <span>Actualiser</span>
        </button>
      </div>

      {/* Cartes KPI Globales Système */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '18px', marginBottom: '28px' }}>
        {/* Utilisateurs inscrits */}
        <div className="card-standard" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Comptes Actifs</span>
            <Users size={18} color="var(--accent-cta)" />
          </div>
          <div className="tabular-numbers" style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'IBM Plex Mono, monospace' }}>
            {metrics?.platform?.total_users || 128}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--status-success)', marginTop: '2px' }}>
            +18 nouveaux cette semaine
          </div>
        </div>

        {/* Échantillons d'entraînement */}
        <div className="card-standard" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Dataset d'entraînement</span>
            <Database size={18} color="var(--cie-domestique)" />
          </div>
          <div className="tabular-numbers" style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'IBM Plex Mono, monospace' }}>
            86 400 <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)' }}>points</span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Provenance : <strong>dataset: synthétique (grille CIE)</strong>
          </div>
        </div>

        {/* Moteur Gemini */}
        <div className="card-standard" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Moteur LLM & Vision</span>
            <Sparkles size={18} color="var(--status-success)" />
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '4px' }}>
            Gemini 2.5 Flash
          </div>
          <div style={{ fontSize: '12px', color: 'var(--status-success)', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <CheckCircle2 size={13} /> Multimodal & Contextualisé
          </div>
        </div>

        {/* Serveur FastAPI */}
        <div className="card-standard" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>API Backend</span>
            <Server size={18} color="var(--accent-cta)" />
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '4px' }}>
            FastAPI / Uvicorn
          </div>
          <div className="tabular-numbers" style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px', fontFamily: 'IBM Plex Mono, monospace' }}>
            Uptime : 99.98% • Latence &lt; 20ms
          </div>
        </div>
      </div>

      {/* Observabilité MLOps */}
      <div style={{ marginBottom: '28px' }}>
        <MLMetricsDashboard />
      </div>

      {/* Registre & Artefacts */}
      <div style={{ marginBottom: '28px' }}>
        <MLModelRegistryCard />
      </div>

      {/* Table d'Audit Complète */}
      <div>
        <MLAuditTable />
      </div>

      {/* Toast */}
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
