'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, Cell, PieChart, Pie, ResponsiveContainer } from 'recharts';
import { Download, CheckCircle, Search, FileText, Loader2, CreditCard } from 'lucide-react';

export default function FacturationPage() {
  const [grossSavings, setGrossSavings] = useState(0);
  const [gainShare, setGainShare] = useState(0);
  const [barData, setBarData] = useState<any[]>([]);
  const [auditTrail, setAuditTrail] = useState<any[]>([]);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState("");

  // Nouveaux états de simulation
  const [downloadState, setDownloadState] = useState<'idle' | 'generating' | 'analyzing' | 'downloading' | 'done'>('idle');
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [paymentStep, setPaymentStep] = useState<'details' | 'processing' | 'success'>('details');
  const [selectedOperator, setSelectedOperator] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isPaid, setIsPaid] = useState(false);
  const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);

  const showNotification = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(""), 3000);
  };

  useEffect(() => {
    const fetchFacturationData = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/facturation');
        const data = await res.json();
        
        if (data) {
          setGrossSavings(data.grossSavings || 0);
          setGainShare(data.gainShare || 0);
          setBarData(data.barData || []);
          setAuditTrail(data.auditTrail || []);
          setInvoices(data.invoices || []);
        }
      } catch (err) {
        console.error("Failed to fetch facturation data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchFacturationData();
  }, []);

  const pieData = [
    { name: 'Retained Savings (90%)', value: 90, color: '#10b981' },
    { name: isPaid ? 'Commission Réglée (10%)' : 'Commission Gain-Share (10%)', value: 10, color: isPaid ? '#3b82f6' : '#06b6d4' },
  ];

  // Simuler le téléchargement
  const simulateDownload = () => {
    if (downloadState !== 'idle') return;
    setDownloadState('generating');
    setTimeout(() => {
      setDownloadState('analyzing');
      setTimeout(() => {
        setDownloadState('downloading');
        setTimeout(() => {
          setDownloadState('done');
          showNotification("Audit PDF généré avec succès.");
          setIsAuditModalOpen(true);
          setTimeout(() => setDownloadState('idle'), 3000);
        }, 1500);
      }, 1500);
    }, 1500);
  };

  // Simuler le paiement
  const openPaymentModal = (op: string) => {
    if (isPaid) {
      showNotification("La facture de ce mois est déjà réglée.");
      return;
    }
    setSelectedOperator(op);
    setPaymentStep('details');
    setPhoneNumber('');
    setIsPaymentModalOpen(true);
  };

  const processPayment = () => {
    if (!phoneNumber) return showNotification("Veuillez entrer un numéro de téléphone.");
    setPaymentStep('processing');
    setTimeout(() => {
      setPaymentStep('success');
      setTimeout(() => {
        setIsPaymentModalOpen(false);
        setIsPaid(true);
        const newInvoice = {
          id: `INV-202610-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`,
          month: 'OCTOBRE 2026',
          amount: `${gainShare.toLocaleString('fr-FR')} FCFA`,
          status: 'Payé'
        };
        setInvoices(prev => [newInvoice, ...prev]);
        
        const newAudit = {
          timestamp: new Date().toISOString(),
          action: `Règlement Commission (${selectedOperator})`,
          ref: `TX_${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
          status: 'Validé'
        };
        setAuditTrail(prev => [newAudit, ...prev]);
        
        showNotification(`Paiement de ${gainShare.toLocaleString('fr-FR')} FCFA validé et retiré avec succès via ${selectedOperator}.`);
      }, 2500);
    }, 3500); // Simulate USSD wait
  };

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '8px', letterSpacing: '0.05em' }}>
          <span style={{ color: 'var(--primary)' }}>Entreprise</span> / Facturation & Transparence
        </div>
        <h1 className="text-gradient" style={{ fontSize: '28px', fontWeight: 800, marginBottom: '8px' }}>Portail de Transparence Financière</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
          Audit en temps réel du modèle de partage à 10% (Gain-Share) sur les économies industrielles.
        </p>
      </div>

      <div className="facturation-grid">
        {/* LEFT COLUMN */}
        <div className="facturation-left-col">
          
          {/* Main Savings Card */}
          <div className="glass-card glow-card" style={{ padding: '32px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>Économies Totales Vérifiées (Ce Mois)</div>
                <div style={{ fontSize: '36px', fontWeight: 800, color: 'var(--primary)', fontFamily: 'Outfit, sans-serif' }}>
                  {grossSavings.toLocaleString('fr-FR', { maximumFractionDigits: 0 })} <span style={{ fontSize: '16px', color: 'var(--text-muted)', fontWeight: 600 }}>FCFA</span>
                </div>
              </div>
              <div style={{ backgroundColor: 'var(--primary-light)', color: 'var(--primary)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '4px 12px', borderRadius: '16px', fontSize: '12px', fontWeight: 700 }}>
                ↗ Dynamique (API)
              </div>
            </div>

            <div style={{ height: '200px', width: '100%', marginBottom: '24px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                  <Bar dataKey="savings" radius={[4, 4, 0, 0]}>
                    {barData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === barData.length - 1 ? 'var(--primary)' : '#6ee7b7'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', borderTop: '1px solid var(--surface-border)', paddingTop: '24px' }}>
              <div style={{ display: 'flex', gap: '48px' }}>
                <div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>Économies Brutes</div>
                  <div style={{ fontSize: '16px', fontWeight: 700 }}>{grossSavings.toLocaleString('fr-FR', { maximumFractionDigits: 0 })} FCFA</div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>Gain-Share (10%)</div>
                  {isPaid ? (
                    <div style={{ fontSize: '16px', fontWeight: 800, color: '#10b981', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <CheckCircle size={16} /> RÉGLÉ (0 FCFA)
                    </div>
                  ) : (
                    <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--primary)' }}>{gainShare.toLocaleString('fr-FR', { maximumFractionDigits: 0 })} FCFA</div>
                  )}
                </div>
              </div>
              <button 
                onClick={simulateDownload} 
                disabled={downloadState !== 'idle'}
                className={downloadState === 'done' ? "btn-secondary" : "btn-primary"} 
                style={{ width: '220px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '12px 24px', border: 'none', cursor: downloadState !== 'idle' ? 'wait' : 'pointer' }}
              >
                {downloadState === 'idle' && <><Download size={16} /> Télécharger l'Audit</>}
                {downloadState === 'generating' && <><Loader2 size={16} className="animate-spin" /> Génération PDF...</>}
                {downloadState === 'analyzing' && <><Loader2 size={16} className="animate-spin" /> Chiffrement AES...</>}
                {downloadState === 'downloading' && <><Loader2 size={16} className="animate-spin" /> Téléchargement...</>}
                {downloadState === 'done' && <><CheckCircle size={16} /> Terminé !</>}
              </button>
            </div>
          </div>

          {/* Audit Trail */}
          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase' }}>Journal d'Audit</h3>
                <span style={{ fontSize: '10px', backgroundColor: 'var(--surface-hover)', padding: '2px 8px', borderRadius: '4px', color: 'var(--text-muted)' }}>0xDF_..A826 AFX</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--primary)', fontSize: '12px', fontWeight: 700 }}>
                <CheckCircle size={14} /> REGISTRE INFALSIFIABLE
              </div>
            </div>

            <table className="audit-table">
              <thead>
                <tr>
                  <th>HORODATAGE (UTC)</th>
                  <th>ACTION</th>
                  <th>RÉFÉRENCE HASH</th>
                  <th>STATUT</th>
                </tr>
              </thead>
              <tbody>
                {auditTrail.map((audit, idx) => (
                  <tr key={idx}>
                    <td style={{ color: 'var(--text-muted)' }}>
                      {audit.timestamp.split('T')[0]}<br/>
                      {audit.timestamp.split('T')[1]}
                    </td>
                    <td style={{ fontWeight: 600, fontSize: '14px' }}>{audit.action}</td>
                    <td style={{ color: 'var(--text-muted)' }}>{audit.ref}</td>
                    <td><span className="status-badge status-verified">● {audit.status}</span></td>
                  </tr>
                ))}
                {auditTrail.length === 0 && !loading && (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)' }}>Aucun audit récent</td>
                  </tr>
                )}
              </tbody>
            </table>
            
            <div style={{ textAlign: 'center', marginTop: '24px' }}>
              <a href="#" onClick={(e) => { e.preventDefault(); showNotification("Connexion à l'explorateur de noeuds en cours..."); }} style={{ color: 'var(--primary)', fontSize: '12px', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', textDecoration: 'none' }}>VOIR LE REGISTRE BLOCKCHAIN COMPLET</a>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div className="facturation-right-col">
          
          {/* Automated Settlement */}
          <div className="glass-card">
            <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '24px', textTransform: 'uppercase' }}>Règlement Automatisé</h3>
            
            <div style={{ border: '1px solid var(--primary-light)', backgroundColor: 'var(--primary-dim)', borderRadius: '8px', padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '32px', height: '24px', backgroundColor: 'var(--foreground)', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <span style={{ color: '#00ffff', fontWeight: 'bold', fontSize: '10px' }}>W</span>
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '14px' }}>Wave</div>
                  <div style={{ fontSize: '11px', color: 'var(--primary)', fontWeight: 700, letterSpacing: '0.05em' }}>CONNECTÉ (PRINCIPAL)</div>
                </div>
              </div>
              {isPaid ? (
                 <CheckCircle color="var(--primary)" size={20} />
              ) : (
                 <span onClick={() => openPaymentModal('Wave')} style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 800, cursor: 'pointer', backgroundColor: 'var(--primary-light)', padding: '6px 12px', borderRadius: '4px' }}>PAYER</span>
              )}
            </div>

            <div style={{ border: '1px solid var(--surface-border)', borderRadius: '8px', padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '32px', height: '24px', backgroundColor: '#FF6600', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <span style={{ color: '#fff', fontWeight: 'bold', fontSize: '10px' }}>O</span>
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '14px' }}>Orange</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.05em' }}>CONFIG. SECOURS</div>
                </div>
              </div>
              <span onClick={() => openPaymentModal('Orange Money')} style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 600, cursor: 'pointer' }}>GÉRER</span>
            </div>

            <div style={{ border: '1px solid var(--surface-border)', borderRadius: '8px', padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', opacity: 0.5 }}>
                <div style={{ width: '32px', height: '24px', backgroundColor: '#FFCC00', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <span style={{ color: 'var(--foreground)', fontWeight: 'bold', fontSize: '10px' }}>M</span>
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '14px' }}>MTN</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.05em' }}>NON CONNECTÉ</div>
                </div>
              </div>
              <span onClick={() => openPaymentModal('MTN Mobile Money')} style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 600, cursor: 'pointer' }}>AJOUTER</span>
            </div>

            <div style={{ border: '1px solid var(--surface-border)', borderRadius: '8px', padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', opacity: 0.5 }}>
                <div style={{ width: '32px', height: '24px', backgroundColor: '#0055A5', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <span style={{ color: '#fff', fontWeight: 'bold', fontSize: '10px' }}>M</span>
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '14px' }}>Moov</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.05em' }}>NON CONNECTÉ</div>
                </div>
              </div>
              <span onClick={() => openPaymentModal('Moov Money')} style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 600, cursor: 'pointer' }}>AJOUTER</span>
            </div>

            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.05em', marginBottom: '8px', textTransform: 'uppercase' }}>PROCHAIN CYCLE DE FACTURATION : 01 OCT 2026</div>
            <div style={{ width: '100%', height: '6px', backgroundColor: 'var(--surface-border)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: '80%', height: '100%', backgroundColor: 'var(--primary)' }}></div>
            </div>
          </div>

          {/* Commission History */}
          <div className="glass-card">
            <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '24px', textTransform: 'uppercase' }}>Historique des Commissions (10%)</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
              {invoices.map((inv) => (
                <div key={inv.id} style={{ border: '1px solid var(--surface-border)', borderRadius: '8px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <FileText color="var(--primary)" size={20} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, fontSize: '13px' }}>{inv.id}</div>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600 }}>{inv.month}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 700, fontSize: '14px' }}>{inv.amount}</div>
                    <div onClick={() => showNotification(`Téléchargement de la facture ${inv.id}...`)} style={{ fontSize: '10px', color: 'var(--primary)', fontWeight: 700, cursor: 'pointer' }}>TÉLÉCHARGER</div>
                  </div>
                </div>
              ))}
              {invoices.length === 0 && !loading && (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px 0' }}>Aucune facture disponible</div>
              )}
            </div>

            {/* Model Distribution */}
            <div style={{ backgroundColor: 'rgba(230,244,234,0.3)', borderRadius: '8px', padding: '16px', border: '1px solid var(--primary-light)' }}>
              <h4 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '16px' }}>RÉPARTITION DU MODÈLE</h4>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ width: '60px', height: '60px', position: 'relative' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={pieData} innerRadius={20} outerRadius={30} dataKey="value" stroke="none">
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 800 }}>
                    90%
                  </div>
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981' }}></div>
                    <div style={{ fontSize: '12px', fontWeight: 600 }}>Économies Conservées (90%)</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: isPaid ? '#3b82f6' : '#06b6d4' }}></div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{isPaid ? 'Commission Réglée (10%)' : 'Commission Gain-Share (10%)'}</div>
                  </div>
                </div>
              </div>
            </div>

          </div>

        </div>
      </div>

      {/* Modal du Rapport d'Audit */}
      {isAuditModalOpen && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 10000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(4px)' }}>
          <div className="glass-card" style={{ width: '800px', height: '80vh', backgroundColor: '#ffffff', padding: '0', borderRadius: '12px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ backgroundColor: '#f1f5f9', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--foreground)' }}>
                <FileText size={24} color="var(--foreground)" />
                <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Rapport_Audit_NouanKanyAI.pdf</h2>
              </div>
              <button onClick={() => setIsAuditModalOpen(false)} style={{ background: 'none', border: 'none', fontSize: '28px', cursor: 'pointer', color: '#64748b' }}>×</button>
            </div>
            <div style={{ padding: '40px', flex: 1, overflowY: 'auto', color: 'var(--foreground)', fontFamily: 'serif' }}>
              <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                <h1 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '8px', color: '#1e293b' }}>RAPPORT D'AUDIT ÉNERGÉTIQUE</h1>
                <p style={{ fontSize: '14px', color: '#64748b' }}>Généré par NouanKanyAI - {new Date().toLocaleDateString('fr-FR')}</p>
              </div>
              <hr style={{ borderColor: '#e2e8f0', marginBottom: '32px' }} />
              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px', color: '#334155' }}>1. Synthèse des Économies</h3>
              <p style={{ marginBottom: '24px', lineHeight: '1.6' }}>
                Ce mois-ci, l'intelligence artificielle de NouanKanyAI a permis d'optimiser la consommation de vos équipements industriels, générant une économie brute certifiée de <strong>{grossSavings.toLocaleString('fr-FR')} FCFA</strong>.
              </p>
              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px', color: '#334155' }}>2. Détail du Gain-Share</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '32px' }}>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '12px 0', fontWeight: 600 }}>Économies Conservées (90%)</td>
                    <td style={{ padding: '12px 0', textAlign: 'right', fontWeight: 700, color: '#10b981' }}>{(grossSavings * 0.9).toLocaleString('fr-FR')} FCFA</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '12px 0', fontWeight: 600 }}>Commission NouanKanyAI (10%)</td>
                    <td style={{ padding: '12px 0', textAlign: 'right', fontWeight: 700 }}>{gainShare.toLocaleString('fr-FR')} FCFA</td>
                  </tr>
                </tbody>
              </table>
              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px', color: '#334155' }}>3. Empreinte Carbone</h3>
              <p style={{ lineHeight: '1.6' }}>
                Grâce à nos optimisations en temps réel, vous avez évité l'émission de plusieurs tonnes de CO2 dans l'atmosphère, contribuant à une industrie plus verte.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Paiement USSD */}
      {isPaymentModalOpen && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(4px)' }}>
          <div className="glass-card" style={{ width: '450px', backgroundColor: 'var(--background)', padding: '32px', borderRadius: '16px', border: '1px solid var(--surface-border)' }}>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '12px', backgroundColor: 'var(--primary-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                 <CreditCard color="var(--primary)" size={24} />
              </div>
              <div>
                <h2 style={{ fontSize: '20px', fontWeight: 800 }}>Portail de Paiement</h2>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)', fontWeight: 600 }}>Règlement sécurisé via {selectedOperator}</div>
              </div>
            </div>
            
            {paymentStep === 'details' && (
              <div>
                 <div style={{ display: 'flex', justifyContent: 'space-between', padding: '16px', backgroundColor: 'var(--surface)', borderRadius: '8px', marginBottom: '24px', border: '1px solid var(--surface-border)' }}>
                   <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Montant dû (10% Gain-Share)</span>
                   <span style={{ fontWeight: 800, color: 'var(--primary)', fontSize: '18px' }}>{gainShare.toLocaleString('fr-FR')} FCFA</span>
                 </div>
                 
                 <div style={{ marginBottom: '24px' }}>
                   <label style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px', display: 'block' }}>Numéro de téléphone de facturation</label>
                   <input 
                     type="text" 
                     value={phoneNumber} 
                     onChange={(e) => setPhoneNumber(e.target.value)} 
                     placeholder="Ex: 01 02 03 04 05" 
                     style={{ width: '100%', padding: '16px', borderRadius: '8px', border: '1px solid var(--surface-border)', backgroundColor: 'var(--surface)', color: 'var(--foreground)', fontSize: '16px', outline: 'none' }} 
                   />
                 </div>
                 
                 <button onClick={processPayment} className="btn-primary" style={{ width: '100%', padding: '16px', borderRadius: '8px', border: 'none', fontWeight: 700, fontSize: '15px', cursor: 'pointer', marginBottom: '12px' }}>
                   Lancer le prélèvement USSD
                 </button>
                 <button onClick={() => setIsPaymentModalOpen(false)} style={{ width: '100%', padding: '12px', borderRadius: '8px', border: 'none', backgroundColor: 'transparent', color: 'var(--text-muted)', fontWeight: 600, cursor: 'pointer' }}>
                   Annuler
                 </button>
              </div>
            )}
            
            {paymentStep === 'processing' && (
              <div style={{ textAlign: 'center', padding: '32px 0' }}>
                 <Loader2 size={64} className="animate-spin" style={{ color: 'var(--primary)', margin: '0 auto 24px auto' }} />
                 <div style={{ fontWeight: 700, fontSize: '18px', marginBottom: '12px' }}>En attente de validation USSD...</div>
                 <div style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: '1.6', maxWidth: '300px', margin: '0 auto' }}>
                   Veuillez consulter votre téléphone ({phoneNumber}) et entrer votre code secret {selectedOperator} pour valider le prélèvement.
                 </div>
              </div>
            )}

            {paymentStep === 'success' && (
              <div style={{ textAlign: 'center', padding: '32px 0' }}>
                 <CheckCircle size={64} color="#10b981" style={{ margin: '0 auto 24px auto' }} />
                 <div style={{ fontWeight: 800, fontSize: '24px', color: '#10b981', marginBottom: '12px' }}>Paiement Validé !</div>
                 <div style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: '1.6', maxWidth: '300px', margin: '0 auto' }}>
                   Le montant de {gainShare.toLocaleString('fr-FR')} FCFA a été prélevé. Votre facture de ce mois est réglée et la commission a été retirée.
                 </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Custom Toast Notification */}
      {notification && (
        <div style={{ 
          position: 'fixed', 
          bottom: '32px', 
          right: '32px', 
          backgroundColor: 'var(--foreground)', 
          color: 'var(--background)', 
          padding: '16px 24px', 
          borderRadius: '8px', 
          fontWeight: 600, 
          zIndex: 1000, 
          boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          animation: 'fadeIn 0.3s ease'
        }}>
          <CheckCircle size={18} color="var(--primary)" />
          {notification}
        </div>
      )}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      `}} />
    </div>
  );
}
