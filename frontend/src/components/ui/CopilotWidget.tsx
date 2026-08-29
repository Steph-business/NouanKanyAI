'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Bot, Send, X, Sparkles, AlertTriangle, ShieldCheck, ChevronUp, ChevronDown, Minimize2 } from 'lucide-react';
import { API_URL } from '@/lib/api';
import { ProvenanceBadge } from './ProvenanceBadge';

interface CopilotWidgetProps {
  onExecuteAction?: (actionText: string) => void;
}

export function CopilotWidget({ onExecuteAction }: CopilotWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{ sender: 'ai' | 'user'; text: string; time: string }>>([
    {
      sender: 'ai',
      text: "Bonjour. Je suis votre Copilot Énergétique NouanKanyAI. Je peux analyser vos appareils, suggérer des délestages ou calculer vos gains selon la tarification CIE.",
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput('');
    const timeNow = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });

    setMessages((prev) => [...prev, { sender: 'user', text: userText, time: timeNow }]);
    setLoading(true);

    try {
      // Récupérer le contexte des machines si disponible
      let machinesState: any[] = [];
      try {
        const res = await fetch(`${API_URL}/api/machines`);
        machinesState = await res.json();
      } catch (err) {
        console.warn("Could not fetch machines context", err);
      }

      const chatRes = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          context: machinesState,
        }),
      });

      const data = await chatRes.json();
      const aiReply = data.response || "Analyse terminée avec succès.";

      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: aiReply,
          time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: "Désolé, une erreur de communication avec le serveur IA est survenue. Veuillez vérifier votre connexion.",
          time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            position: 'fixed',
            bottom: '28px',
            right: '28px',
            zIndex: 9000,
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '12px 20px',
            backgroundColor: 'var(--accent-cta)',
            color: '#FFFFFF',
            borderRadius: 'var(--radius-full)',
            border: 'none',
            boxShadow: 'var(--shadow-dropdown)',
            cursor: 'pointer',
            fontFamily: 'Space Grotesk, sans-serif',
            fontSize: '14px',
            fontWeight: 700,
            transition: 'transform 0.2s ease, box-shadow 0.2s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
          onMouseLeave={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
          aria-label="Ouvrir le Copilot IA"
        >
          <div
            style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Bot size={18} color="#FFFFFF" />
          </div>
          <span>Assistant IA</span>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#34D399', boxShadow: '0 0 6px #34D399' }} />
        </button>
      )}

      {/* Floating Chat Modal */}
      {isOpen && (
        <div
          className="card-standard"
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            width: '380px',
            height: '520px',
            zIndex: 9000,
            padding: 0,
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: 'var(--bg-card)',
            boxShadow: 'var(--shadow-dropdown)',
            borderRadius: 'var(--radius-lg)',
            overflow: 'hidden',
            border: '1px solid var(--border-color)',
            animation: 'fadeIn 0.2s ease-out forwards',
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '14px 18px',
              backgroundColor: 'var(--bg-surface)',
              borderBottom: '1px solid var(--border-color)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--accent-cta)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF',
                }}
              >
                <Bot size={18} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)' }}>
                    Copilot NouanKanyAI
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--status-success)' }} />
                  <span>Connecté aux modèles v2.0</span>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <button
                onClick={() => setIsOpen(false)}
                className="btn-ghost"
                style={{ padding: '6px' }}
                aria-label="Réduire"
              >
                <Minimize2 size={16} />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="btn-ghost"
                style={{ padding: '6px' }}
                aria-label="Fermer"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* Quick suggestions banner */}
          <div
            style={{
              padding: '8px 12px',
              backgroundColor: 'var(--bg-subtle)',
              borderBottom: '1px solid var(--border-subtle)',
              display: 'flex',
              gap: '6px',
              overflowX: 'auto',
            }}
          >
            <button
              onClick={() => {
                setInput("Quelles sont les machines qui consomment le plus actuellement ?");
              }}
              style={{
                fontSize: '11px',
                padding: '4px 8px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
              }}
            >
              📊 Top consommateurs
            </button>
            <button
              onClick={() => {
                setInput("Comment réduire ma facture CIE ce mois-ci ?");
              }}
              style={{
                fontSize: '11px',
                padding: '4px 8px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
              }}
            >
              💡 Conseils CIE
            </button>
          </div>

          {/* Message List */}
          <div
            style={{
              flex: 1,
              padding: '16px',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              backgroundColor: 'var(--bg-primary)',
            }}
          >
            {messages.map((msg, idx) => {
              const isUser = msg.sender === 'user';
              return (
                <div
                  key={idx}
                  style={{
                    alignSelf: isUser ? 'flex-end' : 'flex-start',
                    maxWidth: '85%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: isUser ? 'flex-end' : 'flex-start',
                  }}
                >
                  <div
                    style={{
                      padding: '10px 14px',
                      borderRadius: isUser ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                      backgroundColor: isUser ? 'var(--accent-cta)' : 'var(--bg-card)',
                      color: isUser ? '#FFFFFF' : 'var(--text-primary)',
                      border: isUser ? 'none' : '1px solid var(--border-color)',
                      fontSize: '13px',
                      lineHeight: 1.45,
                      boxShadow: 'var(--shadow-sm)',
                      whiteSpace: 'pre-wrap',
                    }}
                  >
                    {msg.text}
                  </div>
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px', paddingLeft: '4px', paddingRight: '4px' }}>
                    {msg.time}
                  </span>
                </div>
              );
            })}

            {loading && (
              <div
                style={{
                  alignSelf: 'flex-start',
                  padding: '10px 14px',
                  borderRadius: '14px 14px 14px 2px',
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  fontSize: '12px',
                  color: 'var(--text-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <span className="spin-slow">⏳</span>
                <span>Analyse en cours...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form
            onSubmit={handleSend}
            style={{
              padding: '12px',
              backgroundColor: 'var(--bg-surface)',
              borderTop: '1px solid var(--border-color)',
              display: 'flex',
              gap: '8px',
              alignItems: 'center',
            }}
          >
            <input
              type="text"
              placeholder="Posez une question à l'IA..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              style={{
                flex: 1,
                padding: '10px 14px',
                borderRadius: 'var(--radius-full)',
                border: '1px solid var(--border-color)',
                backgroundColor: 'var(--bg-card)',
                color: 'var(--text-primary)',
                fontSize: '13px',
                outline: 'none',
              }}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '50%',
                backgroundColor: 'var(--accent-cta)',
                color: '#FFFFFF',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: !input.trim() || loading ? 'not-allowed' : 'pointer',
                opacity: !input.trim() || loading ? 0.5 : 1,
                transition: 'background-color 0.15s ease',
              }}
              aria-label="Envoyer le message"
            >
              <Send size={16} />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
