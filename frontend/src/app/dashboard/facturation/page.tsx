'use client';

import React, { useState, useEffect } from 'react';
import {
  Receipt,
  Download,
  CreditCard,
  CheckCircle2,
  AlertTriangle,
  Smartphone,
  FileText,
  Clock,
  ArrowRight,
  Eye,
  Percent,
  X,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { API_URL } from '@/lib/api';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';
import { Toast, ToastMessage } from '@/components/ui/Toast';

export default function FacturationPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // USSD / Mobile Money Modal
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<'wave' | 'orange' | 'mtn' | 'moov'>('wave');
  const [phoneNumber, setPhoneNumber] = useState('07 00 11 22 33');
  const [processingPayment, setProcessingPayment] = useState(false);
  const [paymentDone, setPaymentDone] = useState(false);

  // PDF Preview Modal
  const [isPdfModalOpen, setIsPdfModalOpen] = useState(false);

  // Toast
  const [toast, setToast] = useState<ToastMessage | null>(null);

  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    setToast({ id: Date.now().toString(), message, type });
  };

  useEffect(() => {
    const fetchFacturation = async () => {
      try {
        const res = await fetch(`${API_URL}/api/facturation`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error("Erreur facturation:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchFacturation();
  }, []);

  const handleSimulatePayment = (e: React.FormEvent) => {
    e.preventDefault();
    setProcessingPayment(true);

    setTimeout(() => {
      setProcessingPayment(false);
      setPaymentDone(true);
      showToast(`Paiement de ${data?.gainShare?.toLocaleString('fr-FR')} FCFA validé via ${selectedProvider.toUpperCase()}.`, 'success');
      setTimeout(() => {
        setIsPaymentModalOpen(false);
        setPaymentDone(false);
      }, 1800);
    }, 1500);
  };

  const grossSavings = data?.grossSavings || 345000;
  const gainShareCommission = data?.gainShare || 34500;
  const netSavingsClient = grossSavings - gainShareCommission;

  const barData = data?.barData || [
    { month: 'Jan', economies: 280000, commission: 28000 },
    { month: 'Fév', economies: 310000, commission: 31000 },
    { month: 'Mar', economies: 295000, commission: 29500 },
    { month: 'Avr', economies: 345000, commission: 34500 },
  ];

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cta)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Modèle Gain-Share 90 / 10
            </span>
            <ProvenanceBadge type="mesure" label="Règlement Transparent" />
          </div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
            Facturation & Partage d'Économies
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
            Vous conservez 90% des économies mesurées sur votre facture d'électricité.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setIsPdfModalOpen(true)}
            className="btn-outline"
            style={{ fontSize: '12px', padding: '8px 14px' }}
          >
            <FileText size={15} />
            <span>Aperçu Rapport PDF</span>
          </button>
          <button
            onClick={() => setIsPaymentModalOpen(true)}
            className="btn-cta"
            style={{ fontSize: '12px', padding: '8px 16px' }}
          >
            <Smartphone size={15} />
            <span>Régler par Mobile Money</span>
          </button>
        </div>
      </div>

      {/* Cartes KPI Gain-Share */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px', marginBottom: '28px' }}>
        {/* Économies Brutes */}
        <div className="card-standard" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Économies Brutes Réalisées
            </span>
            <ProvenanceBadge type="mesure" label="Ce mois" />
          </div>
          <div className="tabular-numbers" style={{ fontSize: '32px', fontWeight: 800, color: 'var(--status-success)', fontFamily: 'IBM Plex Mono, monospace', marginBottom: '4px' }}>
            +{grossSavings.toLocaleString('fr-FR')} <span style={{ fontSize: '14px' }}>FCFA</span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Réduction mesurée par rapport à votre moyenne historique CIE.
          </div>
        </div>

        {/* Part Conservée par le Client (90%) */}
        <div className="card-standard" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Gain Net Client (90%)
            </span>
            <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--status-success)', backgroundColor: 'var(--status-success-bg)', padding: '2px 8px', borderRadius: '12px' }}>
              Conservé
            </span>
          </div>
          <div className="tabular-numbers" style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'IBM Plex Mono, monospace', marginBottom: '4px' }}>
            {netSavingsClient.toLocaleString('fr-FR')} <span style={{ fontSize: '14px' }}>FCFA</span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Montant directement économisé sur votre trésorerie d'entreprise.
          </div>
        </div>

        {/* Commission NouanKanyAI (10%) */}
        <div className="card-standard" style={{ padding: '24px', borderColor: 'var(--accent-cta)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-cta)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Quote-part NouanKanyAI (10%)
            </span>
            <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cta)', backgroundColor: 'var(--bg-surface)', padding: '2px 8px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              Gain-Share
            </span>
          </div>
          <div className="tabular-numbers" style={{ fontSize: '32px', fontWeight: 800, color: 'var(--accent-cta)', fontFamily: 'IBM Plex Mono, monospace', marginBottom: '4px' }}>
            {gainShareCommission.toLocaleString('fr-FR')} <span style={{ fontSize: '14px' }}>FCFA</span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            À régler mensuellement par Mobile Money après constat des résultats.
          </div>
        </div>
      </div>

      {/* Graphique de Répartition Gain-Share */}
      <div className="card-standard" style={{ padding: '24px', marginBottom: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '8px' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
              Historique des Économies & Partage de Valeur (FCFA)
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
              Comparatif des montants économisés et des commissions mensuelles
            </p>
          </div>
          <div style={{ display: 'flex', gap: '16px', fontSize: '12px', fontWeight: 600 }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '10px', height: '10px', backgroundColor: 'var(--status-success)', borderRadius: '2px' }} />
              Économies Réalisées
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '10px', height: '10px', backgroundColor: 'var(--accent-cta)', borderRadius: '2px' }} />
              Commission (10%)
            </span>
          </div>
        </div>

        <div style={{ height: '260px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--bg-elevated)',
                  borderColor: 'var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  boxShadow: 'var(--shadow-md)',
                }}
                itemStyle={{ fontSize: '12px', fontWeight: 600 }}
                formatter={(value: any) => [`${Number(value).toLocaleString('fr-FR')} FCFA`, '']}
              />
              <Bar dataKey="economies" fill="var(--status-success)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="commission" fill="var(--accent-cta)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tableau des Factures et Traçabilité */}
      <div className="card-standard" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
            Historique des Règlements Gain-Share
          </h3>
          <ProvenanceBadge type="mesure" label="Certifié Conforme" />
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Période</th>
                <th>Économies Constatées</th>
                <th>Montant Commission (10%)</th>
                <th>Mode de Paiement</th>
                <th>Statut</th>
                <th>Justificatif</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 700 }}>Avril 2026</td>
                <td className="tabular-numbers" style={{ fontWeight: 700, color: 'var(--status-success)', fontFamily: 'IBM Plex Mono, monospace' }}>+345 000 FCFA</td>
                <td className="tabular-numbers" style={{ fontWeight: 700, color: 'var(--accent-cta)', fontFamily: 'IBM Plex Mono, monospace' }}>34 500 FCFA</td>
                <td>Wave Mobile Money</td>
                <td>
                  <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--status-success)', backgroundColor: 'var(--status-success-bg)', padding: '2px 8px', borderRadius: '10px' }}>
                    PAYÉ
                  </span>
                </td>
                <td>
                  <button onClick={() => setIsPdfModalOpen(true)} className="btn-ghost" style={{ padding: '4px 8px', fontSize: '11px' }}>
                    Télécharger
                  </button>
                </td>
              </tr>
              <tr>
                <td style={{ fontWeight: 700 }}>Mars 2026</td>
                <td className="tabular-numbers" style={{ fontWeight: 700, color: 'var(--status-success)', fontFamily: 'IBM Plex Mono, monospace' }}>+295 000 FCFA</td>
                <td className="tabular-numbers" style={{ fontWeight: 700, color: 'var(--accent-cta)', fontFamily: 'IBM Plex Mono, monospace' }}>29 500 FCFA</td>
                <td>Orange Money</td>
                <td>
                  <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--status-success)', backgroundColor: 'var(--status-success-bg)', padding: '2px 8px', borderRadius: '10px' }}>
                    PAYÉ
                  </span>
                </td>
                <td>
                  <button onClick={() => setIsPdfModalOpen(true)} className="btn-ghost" style={{ padding: '4px 8px', fontSize: '11px' }}>
                    Télécharger
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* MODAL USSD / MOBILE MONEY */}
      {isPaymentModalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.6)',
            backdropFilter: 'blur(3px)',
            zIndex: 99990,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
          onClick={() => setIsPaymentModalOpen(false)}
        >
          <div
            className="card-standard"
            style={{
              width: '100%',
              maxWidth: '440px',
              backgroundColor: 'var(--bg-elevated)',
              boxShadow: 'var(--shadow-dropdown)',
              borderRadius: 'var(--radius-lg)',
              padding: '28px',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  Règlement Mobile Money
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Commission Gain-Share : <strong>{gainShareCommission.toLocaleString('fr-FR')} FCFA</strong>
                </p>
              </div>
              <button onClick={() => setIsPaymentModalOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={18} />
              </button>
            </div>

            {!paymentDone ? (
              <form onSubmit={handleSimulatePayment} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    Opérateur
                  </label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px' }}>
                    {[
                      { id: 'wave', label: 'Wave' },
                      { id: 'orange', label: 'Orange' },
                      { id: 'mtn', label: 'MTN' },
                      { id: 'moov', label: 'Moov' },
                    ].map((p) => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => setSelectedProvider(p.id as any)}
                        style={{
                          padding: '8px 4px',
                          borderRadius: 'var(--radius-sm)',
                          border: selectedProvider === p.id ? '2px solid var(--accent-cta)' : '1px solid var(--border-color)',
                          backgroundColor: selectedProvider === p.id ? 'var(--bg-surface)' : 'var(--bg-card)',
                          fontSize: '12px',
                          fontWeight: 700,
                          cursor: 'pointer',
                          color: 'var(--text-primary)',
                        }}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                    Numéro de téléphone
                  </label>
                  <input
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="input-standard tabular-numbers"
                    required
                  />
                </div>

                <div style={{ padding: '12px', backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)', fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  📱 Une invite USSD sera envoyée sur votre téléphone pour valider le prélèvement sécurisé sans frais supplémentaires.
                </div>

                <button
                  type="submit"
                  disabled={processingPayment}
                  className="btn-cta"
                  style={{ width: '100%', marginTop: '6px' }}
                >
                  {processingPayment ? 'Génération de la transaction USSD...' : `Confirmer (${gainShareCommission.toLocaleString('fr-FR')} FCFA)`}
                </button>
              </form>
            ) : (
              <div style={{ padding: '24px', textAlign: 'center' }}>
                <CheckCircle2 size={40} color="var(--status-success)" style={{ margin: '0 auto 12px auto' }} />
                <h4 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>Paiement Confirmé !</h4>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Votre reçu a été généré et archivé dans votre historique d'audit.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODAL RAPPORT AUDIT PDF */}
      {isPdfModalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.6)',
            backdropFilter: 'blur(3px)',
            zIndex: 99990,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
          onClick={() => setIsPdfModalOpen(false)}
        >
          <div
            className="card-standard"
            style={{
              width: '100%',
              maxWidth: '680px',
              maxHeight: '90vh',
              backgroundColor: 'var(--bg-elevated)',
              boxShadow: 'var(--shadow-dropdown)',
              borderRadius: 'var(--radius-lg)',
              padding: 0,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header modal */}
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={18} color="var(--accent-cta)" />
                <span style={{ fontSize: '15px', fontWeight: 800 }}>Rapport d'Audit Énergétique Certifié</span>
              </div>
              <button onClick={() => setIsPdfModalOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={18} />
              </button>
            </div>

            {/* Document preview */}
            <div style={{ padding: '28px', overflowY: 'auto', backgroundColor: '#FFFFFF', color: '#111827', fontFamily: 'Inter, sans-serif' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '2px solid #E5E7EB', paddingBottom: '16px', marginBottom: '20px' }}>
                <div>
                  <h2 style={{ fontSize: '20px', fontWeight: 800, margin: 0, color: '#111827' }}>NouanKanyAI Energy Audit</h2>
                  <div style={{ fontSize: '12px', color: '#6B7280' }}>Plateforme d'optimisation énergétique CIE</div>
                </div>
                <div style={{ textAlign: 'right', fontSize: '11px', color: '#6B7280' }}>
                  <div>Rapport N° : NK-2026-04-098</div>
                  <div>Date : {new Date().toLocaleDateString('fr-FR')}</div>
                </div>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '8px', color: '#374151' }}>1. Synthèse de Facturation CIE</h4>
                <table style={{ width: '100%', fontSize: '12px', borderCollapse: 'collapse' }}>
                  <tbody>
                    <tr style={{ borderBottom: '1px solid #E5E7EB' }}>
                      <td style={{ padding: '6px 0', color: '#6B7280' }}>Consommation de référence :</td>
                      <td style={{ padding: '6px 0', fontWeight: 700, textAlign: 'right' }}>5 073 kWh</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid #E5E7EB' }}>
                      <td style={{ padding: '6px 0', color: '#6B7280' }}>Consommation optimisée :</td>
                      <td style={{ padding: '6px 0', fontWeight: 700, textAlign: 'right' }}>4 000 kWh</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid #E5E7EB' }}>
                      <td style={{ padding: '6px 0', color: '#6B7280' }}>Économie brute réalisée :</td>
                      <td style={{ padding: '6px 0', fontWeight: 800, color: '#15803D', textAlign: 'right' }}>+345 000 FCFA</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '6px 0', color: '#6B7280' }}>Quote-part Gain-Share (10%) :</td>
                      <td style={{ padding: '6px 0', fontWeight: 800, color: '#C2410C', textAlign: 'right' }}>34 500 FCFA</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div>
                <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '8px', color: '#374151' }}>2. Actions d'Optimisation Appliquées</h4>
                <ul style={{ fontSize: '12px', color: '#4B5563', paddingLeft: '16px', lineHeight: 1.6 }}>
                  <li>Délestage préventif des compresseurs aux heures de pointe (18h-22h).</li>
                  <li>Régulation thermique automatique sur chambre froide 01.</li>
                  <li>Détection et résolution d'une surchauffe anormale sur moteur broyeur.</li>
                </ul>
              </div>
            </div>

            {/* Footer modal */}
            <div style={{ padding: '14px 20px', borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-surface)', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button
                onClick={() => {
                  showToast("Téléchargement du rapport PDF initié.", 'success');
                  setIsPdfModalOpen(false);
                }}
                className="btn-cta"
              >
                <Download size={15} />
                <span>Télécharger le PDF Certifié</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast */}
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
