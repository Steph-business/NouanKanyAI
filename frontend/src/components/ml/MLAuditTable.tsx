'use client';

/**
 * components/ml/MLAuditTable.tsx — Tableau d'audit et traçabilité des inférences IA en direct.
 */

import React, { useState } from 'react';
import { History, CheckCircle2, AlertTriangle, XCircle, RefreshCw, Filter, ShieldCheck } from 'lucide-react';
import { useMLAuditLogs } from '@/hooks/use-ml';

export function MLAuditTable() {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [operationFilter, setOperationFilter] = useState<string>('');
  const [limit, setLimit] = useState<number>(15);

  const { logs, loading, refresh } = useMLAuditLogs({
    limit,
    status: statusFilter || undefined,
    operation: operationFilter || undefined,
    autoRefresh: true,
    interval: 8000,
  });

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(2, 132, 199, 0.25))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#059669',
            }}
          >
            <History size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, margin: 0, color: 'var(--foreground)' }}>
              Journal d'Audit des Inférences IA
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-subtle)', margin: 0 }}>
              Traçabilité déterministe, horodatage UTC et latence par requête
            </p>
          </div>
        </div>

        {/* Filtres rapides */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          <select
            value={operationFilter}
            onChange={(e) => setOperationFilter(e.target.value)}
            style={{
              padding: '6px 10px',
              borderRadius: '6px',
              border: '1px solid var(--surface-border)',
              background: 'var(--surface-2)',
              fontSize: '11px',
              color: 'var(--foreground)',
            }}
          >
            <option value="">Toutes Opérations</option>
            <option value="forecasting">Prévisions (XGBoost)</option>
            <option value="anomaly_detection">Anomalies (Isolation Forest)</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: '6px 10px',
              borderRadius: '6px',
              border: '1px solid var(--surface-border)',
              background: 'var(--surface-2)',
              fontSize: '11px',
              color: 'var(--foreground)',
            }}
          >
            <option value="">Tous Statuts</option>
            <option value="SUCCESS">Succès (SUCCESS)</option>
            <option value="VALIDATION_FAILED">Validation Échouée</option>
            <option value="ERROR">Erreur (ERROR)</option>
          </select>

          <button
            onClick={() => refresh()}
            style={{
              padding: '6px 10px',
              borderRadius: '6px',
              border: '1px solid var(--surface-border)',
              background: 'var(--surface)',
              fontSize: '11px',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <RefreshCw size={11} />
            <span>Rafraîchir</span>
          </button>
        </div>
      </div>

      {/* Table responsive */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--surface-border)', color: 'var(--text-subtle)', fontSize: '11px' }}>
              <th style={{ padding: '8px 10px' }}>Horodatage</th>
              <th style={{ padding: '8px 10px' }}>Opération</th>
              <th style={{ padding: '8px 10px' }}>Modèle</th>
              <th style={{ padding: '8px 10px' }}>Latence</th>
              <th style={{ padding: '8px 10px' }}>Statut</th>
              <th style={{ padding: '8px 10px' }}>Request ID</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: '24px', textAlign: 'center', color: 'var(--text-subtle)' }}>
                  {loading ? "Chargement des enregistrements d'audit..." : "Aucune transaction d'inférence enregistrée."}
                </td>
              </tr>
            ) : (
              logs.map((record) => {
                const date = new Date(record.timestamp);
                const formattedTime = date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                const isSuccess = record.status === 'SUCCESS';
                const isValFailed = record.status === 'VALIDATION_FAILED';

                return (
                  <tr key={record.audit_id} style={{ borderBottom: '1px solid var(--surface-border)' }}>
                    <td style={{ padding: '8px 10px', fontWeight: 600, color: 'var(--foreground)' }}>
                      {formattedTime}
                    </td>
                    <td style={{ padding: '8px 10px', fontWeight: 600 }}>
                      <span
                        style={{
                          padding: '2px 8px',
                          borderRadius: '4px',
                          background: record.operation === 'forecasting' ? 'rgba(5, 150, 105, 0.08)' : 'rgba(234, 88, 12, 0.08)',
                          color: record.operation === 'forecasting' ? '#059669' : '#ea580c',
                        }}
                      >
                        {record.operation === 'forecasting' ? 'Prévision' : 'Anomalie'}
                      </span>
                    </td>
                    <td style={{ padding: '8px 10px', color: 'var(--text-muted)' }}>
                      {record.model_name.replace('_', ' ')}
                    </td>
                    <td style={{ padding: '8px 10px', fontWeight: 700, color: record.execution_time_ms < 50 ? '#059669' : '#ea580c' }}>
                      {record.execution_time_ms} ms
                    </td>
                    <td style={{ padding: '8px 10px' }}>
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '11px',
                          fontWeight: 700,
                          color: isSuccess ? '#059669' : isValFailed ? '#d97706' : '#dc2626',
                        }}
                      >
                        {isSuccess ? <CheckCircle2 size={13} /> : isValFailed ? <AlertTriangle size={13} /> : <XCircle size={13} />}
                        {record.status}
                      </span>
                    </td>
                    <td style={{ padding: '8px 10px', color: 'var(--text-subtle)', fontFamily: 'monospace', fontSize: '11px' }}>
                      {record.request_id ? `${record.request_id.slice(0, 8)}...` : 'N/A'}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
