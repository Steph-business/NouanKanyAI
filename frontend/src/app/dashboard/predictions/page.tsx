'use client';

/**
 * app/dashboard/predictions/page.tsx — Plateforme Intégrée d'Intelligence Artificielle de NouanKanyAI.
 * 
 * Combine :
 * - Assistant Copilot & Actions physiques recommandées
 * - Moteur d'inférence en direct (XGBoost Forecaster & Isolation Forest)
 * - Télémétrie & observabilité opérationnelle temps réel
 * - Registre de modèles, versions et journal d'audit
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Bot,
  Send,
  Sparkles,
  Zap,
  ShieldAlert,
  Loader2,
  Cpu,
  Activity,
  Database,
  History,
  TrendingUp,
} from 'lucide-react';
import { API_URL } from '@/lib/api';
import {
  MLHealthBadge,
  ForecastingWidget,
  AnomalyDetectorWidget,
  MLMetricsDashboard,
  MLModelRegistryCard,
  MLAuditTable,
} from '@/components/ml';

type TabType = 'copilot' | 'inference' | 'metrics' | 'registry';

export default function PredictionsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('copilot');
  const [inputMessage, setInputMessage] = useState('');
  
  const getCurrentTime = () => {
    const now = new Date();
    const dateStr = now.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
    const timeStr = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    return `${dateStr} à ${timeStr}`;
  };

  const defaultMessage = {
    sender: 'ai',
    text: 'Bonjour ! Je suis votre Assistant IA NouanKanyAI. Je suis connecté à vos modèles XGBoost v2.0.0 et Isolation Forest v2.0.0 en temps réel. Comment puis-je vous aider ?',
    timestamp: getCurrentTime(),
  };

  const [messages, setMessages] = useState<any[]>([defaultMessage]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loadingRecs, setLoadingRecs] = useState(true);
  const [executingId, setExecutingId] = useState<string | null>(null);

  // Notifications Toast
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState<'info' | 'error' | 'success'>('info');

  const showToast = (msg: string, type: 'info' | 'error' | 'success' = 'info') => {
    setToastMessage(msg);
    setToastType(type);
    setTimeout(() => setToastMessage(''), 3500);
  };

  // Chargement des recommandations
  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const machinesRes = await fetch(`${API_URL}/api/machines`);
        const currentMachinesState = await machinesRes.json();

        const response = await fetch(`${API_URL}/api/recommend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(currentMachinesState),
        });

        const data = await response.json();
        if (data.recommendations) {
          setRecommendations(data.recommendations);
        }
      } catch (error) {
        console.error("Erreur lors de la récupération des recommandations:", error);
      } finally {
        setLoadingRecs(false);
      }
    };

    fetchRecommendations();
  }, []);

  const handleSend = async () => {
    if (!inputMessage.trim()) return;

    const userMsg = inputMessage;
    setMessages((prev) => [...prev, { sender: 'user', text: userMsg, timestamp: getCurrentTime() }]);
    setInputMessage('');

    setMessages((prev) => [...prev, { sender: 'ai', text: '...', timestamp: getCurrentTime() }]);

    try {
      const machinesRes = await fetch(`${API_URL}/api/machines`);
      const currentMachinesState = await machinesRes.json();

      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, context: currentMachinesState }),
      });

      const data = await response.json();

      setMessages((prev) => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = {
          sender: 'ai',
          text: data.response,
          timestamp: getCurrentTime(),
        };
        return newMsgs;
      });
    } catch (error) {
      setMessages((prev) => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = {
          sender: 'ai',
          text: "Erreur de connexion à l'IA NouanKanyAI.",
          timestamp: getCurrentTime(),
        };
        return newMsgs;
      });
    }
  };

  const executeAction = async (rec: any) => {
    if (executingId) return;

    const actionId = rec.machine_id + rec.type;
    setExecutingId(actionId);

    try {
      if (rec.type === 'alerte') {
        showToast(`Coupure d'urgence de ${rec.machine_id} en cours...`, 'error');
        await fetch(`${API_URL}/api/machines/${rec.machine_id}/toggle`, { method: 'POST' });
      } else if (rec.type === 'optimisation') {
        showToast(`Activation du mode Éco sur ${rec.machine_id}...`, 'info');
        await fetch(`${API_URL}/api/machines/${rec.machine_id}/eco`, { method: 'POST' });
      } else if (rec.type === 'délestage') {
        showToast(`Délestage préventif de ${rec.machine_id} en cours...`, 'info');
        await fetch(`${API_URL}/api/machines/${rec.machine_id}/toggle`, { method: 'POST' });
      }

      const actionText = `Exécute l'action recommandée : "${rec.action}" sur l'équipement ${rec.machine_id}.`;

      setMessages((prev) => [...prev, { sender: 'user', text: actionText, timestamp: getCurrentTime() }]);
      setMessages((prev) => [...prev, { sender: 'ai', text: "Exécution de la commande en cours...", timestamp: getCurrentTime() }]);

      const machinesRes = await fetch(`${API_URL}/api/machines`);
      const currentMachinesState = await machinesRes.json();

      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `L'utilisateur vient d'exécuter l'action physique : ${rec.action} sur ${rec.machine_id}. Confirme brièvement et professionnellement que l'intervention est un succès et que le système est sécurisé/optimisé.`,
          context: currentMachinesState,
        }),
      });

      const data = await response.json();

      setMessages((prev) => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = {
          sender: 'ai',
          text: data.response,
          timestamp: getCurrentTime(),
        };
        return newMsgs;
      });

      setRecommendations((prev) => prev.filter((r) => r.machine_id !== rec.machine_id || r.type !== rec.type));
      showToast('Intervention réussie.', 'success');
    } catch (error) {
      console.error(error);
      setMessages((prev) => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = {
          sender: 'ai',
          text: "Erreur technique lors de l'exécution de l'action physique.",
          timestamp: getCurrentTime(),
        };
        return newMsgs;
      });
      showToast("Erreur lors de l'exécution.", 'error');
    } finally {
      setExecutingId(null);
    }
  };

  const getIconForType = (type: string, severity: string) => {
    if (severity === 'critique') return <ShieldAlert size={20} color="#DC2626" />;
    if (type === 'optimisation') return <Sparkles size={20} color="var(--primary)" />;
    if (type === 'délestage') return <Zap size={20} color="var(--accent)" />;
    return <Bot size={20} color="var(--primary)" />;
  };

  const formatText = (text: string) => {
    if (!text) return '';
    return text
      .replace(/###/g, '')
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*/g, '•');
  };

  return (
    <div>
      {/* Header avec Statut ML en direct */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '6px', letterSpacing: '0.05em' }}>
            <span style={{ color: 'var(--primary)' }}>Intelligence Artificielle</span> / Moteurs & Copilot
          </div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, color: 'var(--foreground)' }}>
            Plateforme IA NouanKanyAI
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginTop: '4px' }}>
            Inférence énergétique XGBoost, détection d'anomalies Isolation Forest et observabilité en temps réel.
          </p>
        </div>

        <MLHealthBadge showDetails={true} />
      </div>

      {/* Barre de navigation par onglets */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          borderBottom: '1px solid var(--surface-border)',
          marginBottom: '24px',
          overflowX: 'auto',
          paddingBottom: '2px',
        }}
      >
        {[
          { id: 'copilot', label: 'Copilot & Recommandations', icon: Bot },
          { id: 'inference', label: 'Moteurs Inférence (XGBoost & Anomaly)', icon: Cpu },
          { id: 'metrics', label: 'Observabilité & Télémétrie', icon: Activity },
          { id: 'registry', label: 'Registre & Journal Audit', icon: Database },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 16px',
                borderRadius: '8px 8px 0 0',
                border: 'none',
                borderBottom: isActive ? '3px solid #059669' : '3px solid transparent',
                background: isActive ? 'var(--surface)' : 'transparent',
                color: isActive ? 'var(--foreground)' : 'var(--text-muted)',
                fontWeight: isActive ? 700 : 500,
                fontSize: '13px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                whiteSpace: 'nowrap',
              }}
            >
              <Icon size={16} color={isActive ? '#059669' : 'currentColor'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Contenu selon l'onglet actif */}

      {/* 1. Onglet Copilot & Recommandations */}
      {activeTab === 'copilot' && (
        <div className="grid-2-equal predictions-grid" style={{ height: '600px' }}>
          {/* Chat Interface */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--surface-border)', backgroundColor: 'var(--surface)', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ backgroundColor: 'var(--primary)', padding: '8px', borderRadius: '50%' }}>
                <Bot color="#fff" size={20} />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '14px' }}>NouanKanyAI Copilot</div>
                <div style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 600 }}>● En ligne et synchronisé (FastAPI v2.0.0)</div>
              </div>
            </div>

            <div style={{ flex: 1, padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px', backgroundColor: 'var(--background-alt)' }}>
              {messages.map((msg, idx) => (
                <div key={idx} style={{ alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start', maxWidth: '80%', display: 'flex', flexDirection: 'column' }}>
                  <div
                    style={{
                      fontSize: '11px',
                      color: 'var(--text-muted)',
                      marginBottom: '6px',
                      textAlign: msg.sender === 'user' ? 'right' : 'left',
                      fontWeight: 500,
                      letterSpacing: '0.02em',
                    }}
                  >
                    {msg.sender === 'user' ? 'Vous' : 'NouanKanyAI'} • {msg.timestamp || getCurrentTime()}
                  </div>
                  <div
                    style={{
                      backgroundColor: msg.sender === 'user' ? 'var(--primary)' : 'var(--surface)',
                      color: msg.sender === 'user' ? '#fff' : 'var(--foreground)',
                      padding: '12px 16px',
                      borderRadius: '12px',
                      border: msg.sender === 'ai' ? '1px solid var(--surface-border)' : 'none',
                      fontSize: '14px',
                      lineHeight: '1.5',
                      whiteSpace: 'pre-wrap',
                    }}
                  >
                    {formatText(msg.text)}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ padding: '16px', borderTop: '1px solid var(--surface-border)', backgroundColor: 'var(--surface)', display: 'flex', gap: '12px' }}>
              <input
                type="text"
                className="chat-input"
                placeholder="Demandez une analyse, un rapport, ou une prédiction..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                style={{ flex: 1, padding: '12px 16px', borderRadius: '24px', border: 'none', outline: 'none', backgroundColor: 'var(--primary)', color: '#ffffff' }}
              />
              <button
                onClick={handleSend}
                style={{
                  backgroundColor: 'var(--primary)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '50%',
                  width: '48px',
                  height: '48px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                }}
              >
                <Send size={18} />
              </button>
            </div>
          </div>

          {/* Actionable Recommendations */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto', paddingRight: '8px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
              RECOMMANDATIONS DE L'IA ({recommendations.length})
              {loadingRecs && <Loader2 size={16} className="animate-spin text-primary" />}
            </h3>

            {!loadingRecs && recommendations.length === 0 ? (
              <div className="glass-card" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                Aucune recommandation critique pour le moment. Vos équipements fonctionnent de manière optimale !
              </div>
            ) : (
              recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  style={{
                    backgroundColor: 'var(--surface)',
                    border: '1px solid var(--surface-border)',
                    borderRadius: '6px',
                    padding: '20px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                  }}
                >
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <div>{getIconForType(rec.type, rec.severity)}</div>
                    <div style={{ fontWeight: 700, fontSize: '15px' }}>{rec.title}</div>
                  </div>

                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                    {rec.description}
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      backgroundColor: 'rgba(0,0,0,0.2)',
                      padding: '12px 16px',
                      borderRadius: '6px',
                      border: '1px solid rgba(255,255,255,0.05)',
                      marginTop: '4px',
                    }}
                  >
                    {rec.gain_fcfa > 0 ? (
                      <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--primary)' }}>
                        Gain : +{rec.gain_fcfa.toLocaleString('fr-FR')} FCFA
                      </div>
                    ) : (
                      <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-muted)' }}>
                        Intervention requise
                      </div>
                    )}
                    <button
                      onClick={() => executeAction(rec)}
                      disabled={executingId === rec.machine_id + rec.type}
                      className={rec.severity === 'critique' ? 'btn-secondary' : 'btn-primary'}
                      style={{
                        width: 'auto',
                        padding: '8px 16px',
                        fontSize: '12px',
                        cursor: executingId === rec.machine_id + rec.type ? 'wait' : 'pointer',
                        borderRadius: '4px',
                        opacity: executingId === rec.machine_id + rec.type ? 0.7 : 1,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      {executingId === rec.machine_id + rec.type ? <Loader2 size={14} className="animate-spin" /> : null}
                      {executingId === rec.machine_id + rec.type ? 'En cours...' : rec.action}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* 2. Onglet Moteurs Inférence (XGBoost & Isolation Forest) */}
      {activeTab === 'inference' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
          <ForecastingWidget />
          <AnomalyDetectorWidget />
        </div>
      )}

      {/* 3. Onglet Observabilité & Télémétrie */}
      {activeTab === 'metrics' && (
        <div>
          <MLMetricsDashboard />
        </div>
      )}

      {/* 4. Onglet Registre & Audit Trail */}
      {activeTab === 'registry' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <MLModelRegistryCard />
          <MLAuditTable />
        </div>
      )}

      {/* Custom Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: 'fixed',
            bottom: '32px',
            right: '32px',
            backgroundColor: toastType === 'error' ? '#ef4444' : toastType === 'success' ? '#10b981' : '#3b82f6',
            color: '#fff',
            padding: '16px 24px',
            borderRadius: '12px',
            fontWeight: 600,
            zIndex: 99999,
            boxShadow: `0 10px 30px ${toastType === 'error' ? 'rgba(239, 68, 68, 0.3)' : toastType === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(59, 130, 246, 0.3)'}`,
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            animation: 'fadeInUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          }}
        >
          <span style={{ fontSize: '18px' }}>{toastType === 'error' ? '⚠' : toastType === 'success' ? '✓' : 'ℹ'}</span>
          {toastMessage}
        </div>
      )}

      <style
        dangerouslySetInnerHTML={{
          __html: `
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `,
        }}
      />
    </div>
  );
}
