'use client';

import React, { useState } from 'react';
import { Bot, Sparkles, Send, Cpu, Activity, History, Layers } from 'lucide-react';
import {
  ForecastingWidget,
  AnomalyDetectorWidget,
  MLMetricsDashboard,
  MLModelRegistryCard,
  MLAuditTable,
} from '@/components/ml';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';
import { API_URL } from '@/lib/api';

export default function PredictionsPage() {
  const [activeTab, setActiveTab] = useState<'copilot' | 'inference' | 'observability' | 'registry' | 'audit'>('copilot');

  // Copilot chat state
  const [messages, setMessages] = useState<Array<{ sender: 'ai' | 'user'; text: string; time: string }>>([
    {
      sender: 'ai',
      text: "Bonjour. Je suis votre Copilot Énergétique NouanKanyAI. Je peux analyser vos courbes de puissance, recommander des réglages selon le barème CIE et auditer vos équipements en temps réel.",
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [loadingChat, setLoadingChat] = useState(false);

  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loadingChat) return;

    const userText = input.trim();
    setInput('');
    const timeNow = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });

    setMessages((prev) => [...prev, { sender: 'user', text: userText, time: timeNow }]);
    setLoadingChat(true);

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText }),
      });
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: data.response || "Analyse complétée.",
          time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: "Erreur de communication avec le serveur IA.",
          time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoadingChat(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cta)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Intelligence Artificielle & MLOps
            </span>
            <ProvenanceBadge type="synthetique" label="Inférence v2.0" />
          </div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
            Assistant IA & Moteurs Prédictifs
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
            Interagissez avec le Copilot ou exploitez directement les modèles XGBoost et Isolation Forest.
          </p>
        </div>
      </div>

      {/* Navigation par Onglets */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          borderBottom: '1px solid var(--border-color)',
          marginBottom: '28px',
          overflowX: 'auto',
        }}
      >
        {[
          { id: 'copilot', label: 'Assistant Conversationnel', icon: Bot },
          { id: 'inference', label: 'Inférences Interactives (XGBoost / Isolation)', icon: Cpu },
          { id: 'observability', label: 'Observabilité MLOps', icon: Activity },
          { id: 'registry', label: 'Registre des Modèles', icon: Layers },
          { id: 'audit', label: 'Journal d\'Audit', icon: History },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 18px',
                border: 'none',
                background: 'transparent',
                fontSize: '13px',
                fontWeight: isActive ? 700 : 500,
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                borderBottom: isActive ? '2px solid var(--accent-cta)' : '2px solid transparent',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'color 0.15s ease',
              }}
            >
              <Icon size={16} color={isActive ? 'var(--accent-cta)' : 'currentColor'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Onglet 1 : Copilot Chat */}
      {activeTab === 'copilot' && (
        <div className="card-standard" style={{ padding: 0, overflow: 'hidden', height: '600px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '16px 20px', backgroundColor: 'var(--bg-surface)', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Bot size={20} color="var(--accent-cta)" />
              <div>
                <span style={{ fontSize: '14px', fontWeight: 800 }}>Copilot NouanKanyAI (Gemini 2.5 Flash)</span>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Contextualisé avec vos équipements et la grille CIE</div>
              </div>
            </div>
            <ProvenanceBadge type="synthetique" label="Inférence LLM" />
          </div>

          {/* Messages */}
          <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '14px', backgroundColor: 'var(--bg-primary)' }}>
            {messages.map((msg, idx) => {
              const isUser = msg.sender === 'user';
              return (
                <div
                  key={idx}
                  style={{
                    alignSelf: isUser ? 'flex-end' : 'flex-start',
                    maxWidth: '75%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: isUser ? 'flex-end' : 'flex-start',
                  }}
                >
                  <div
                    style={{
                      padding: '12px 16px',
                      borderRadius: isUser ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                      backgroundColor: isUser ? 'var(--accent-cta)' : 'var(--bg-card)',
                      color: isUser ? '#FFFFFF' : 'var(--text-primary)',
                      border: isUser ? 'none' : '1px solid var(--border-color)',
                      fontSize: '13px',
                      lineHeight: 1.5,
                      boxShadow: 'var(--shadow-sm)',
                    }}
                  >
                    {msg.text}
                  </div>
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>
                    {msg.time}
                  </span>
                </div>
              );
            })}
            {loadingChat && (
              <div style={{ alignSelf: 'flex-start', padding: '10px 14px', borderRadius: '12px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', fontSize: '12px', color: 'var(--text-muted)' }}>
                Copilot réfléchit...
              </div>
            )}
          </div>

          {/* Chat input */}
          <form onSubmit={handleSendChat} style={{ padding: '14px 20px', backgroundColor: 'var(--bg-surface)', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '10px' }}>
            <input
              type="text"
              placeholder="Posez une question sur vos coûts, machines ou prévisions..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="input-standard"
              style={{ flex: 1 }}
            />
            <button type="submit" disabled={!input.trim() || loadingChat} className="btn-cta">
              <Send size={15} />
              <span>Envoyer</span>
            </button>
          </form>
        </div>
      )}

      {/* Onglet 2 : Inférences XGBoost & Isolation Forest */}
      {activeTab === 'inference' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px' }}>
          <ForecastingWidget />
          <AnomalyDetectorWidget />
        </div>
      )}

      {/* Onglet 3 : Observabilité MLOps */}
      {activeTab === 'observability' && (
        <MLMetricsDashboard />
      )}

      {/* Onglet 4 : Registre des modèles */}
      {activeTab === 'registry' && (
        <MLModelRegistryCard />
      )}

      {/* Onglet 5 : Journal d'Audit */}
      {activeTab === 'audit' && (
        <MLAuditTable />
      )}
    </div>
  );
}
