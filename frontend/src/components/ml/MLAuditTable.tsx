'use client';

import React, { useState } from 'react';
import { History, CheckCircle2, AlertTriangle, XCircle, RefreshCw } from 'lucide-react';
import { useMLAuditLogs } from '@/hooks/use-ml';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';

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
    <div className="card-standard" style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
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
            <History size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
                Journal d'Audit des Inférences IA
              </h3>
              <ProvenanceBadge type="mesure" label="Horodaté UTC" />
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
              Traçabilité déterministe avec hachage cryptographique et latence
            </p>
          </div>
        </div>

        {/* Filtres rapides */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          <select
            value={operationFilter}
            onChange={(e) => setOperationFilter(e.target.value)}
            className="input-standard"
            style={{ minHeight: '34px', padding: '4px 10px', fontSize: '12px', width: 'auto' }}
          >
            <option value="">Toutes Opérations</option>
            <option value="forecasting">Prévisions (XGBoost)</option>
            <option value="anomaly_detection">Anomalies (Isolation Forest)</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-standard"
            style={{ minHeight: '34px', padding: '4px 10px', fontSize: '12px', width: 'auto' }}
          >
            <option value="">Tous Statuts</option>
            <option value="SUCCESS">Succès (SUCCESS)</option>
            <option value="VALIDATION_FAILED">Validation Échouée</option>
            <option value="ERROR">Erreur (ERROR)</option>
          </select>

          <button
            onClick={() => refresh()}
            className="btn-ghost"
            style={{ minHeight: '34px', padding: '4px 10px', fontSize: '11px', border: '1px solid var(--border-color)' }}
          >
            <RefreshCw size={11} />
            <span>Rafraîchir</span>
          </button>
        </div>
      </div>

      {/* Table responsive */}
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Horodatage</th>
              <th>Opération</th>
              <th>Modèle</th>
              <th>Latence</th>
              <th>Statut</th>
              <th>Request ID</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: '24px', textAlign: 'center', color: 'var(--text-secondary)' }}>
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
                  <tr key={record.audit_id}>
                    <td className="tabular-numbers" style={{ fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'IBM Plex Mono, monospace' }}>
                      {formattedTime}
                    </td>
                    <td style={{ fontWeight: 600 }}>
                      <span
                        style={{
                          padding: '2px 8px',
                          borderRadius: '4px',
                          backgroundColor: record.operation === 'forecasting' ? 'var(--status-success-bg)' : 'var(--status-warning-bg)',
                          color: record.operation === 'forecasting' ? 'var(--status-success)' : 'var(--status-warning)',
                          fontSize: '11px',
                          fontWeight: 700,
                        }}
                      >
                        {record.operation === 'forecasting' ? 'Prévision' : 'Anomalie'}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
                      {record.model_name.replace('_', ' ')}
                    </td>
                    <td className="tabular-numbers" style={{ fontWeight: 700, color: record.execution_time_ms < 50 ? 'var(--status-success)' : 'var(--accent-cost)', fontFamily: 'IBM Plex Mono, monospace' }}>
                      {record.execution_time_ms} ms
                    </td>
                    <td>
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '11px',
                          fontWeight: 800,
                          color: isSuccess ? 'var(--status-success)' : isValFailed ? 'var(--status-warning)' : 'var(--status-alert)',
                        }}
                      >
                        {isSuccess ? <CheckCircle2 size={13} /> : isValFailed ? <AlertTriangle size={13} /> : <XCircle size={13} />}
                        {record.status}
                      </span>
                    </td>
                    <td className="tabular-numbers" style={{ color: 'var(--text-muted)', fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px' }}>
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
