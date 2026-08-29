'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Search, LayoutDashboard, Plug, Bot, Receipt, Factory, Settings, Power, Leaf, AlertTriangle, ShieldCheck, X } from 'lucide-react';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectLevel?: (level: 'debutant' | 'amateur' | 'technique') => void;
}

export function CommandPalette({ isOpen, onClose, onSelectLevel }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else onClose(); // parent handles toggle
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const actions = [
    {
      category: 'Navigation',
      items: [
        { label: 'Tableau de bord principal', icon: LayoutDashboard, action: () => { router.push('/dashboard'); onClose(); } },
        { label: 'Gestion des Équipements', icon: Plug, action: () => { router.push('/dashboard/appareils'); onClose(); } },
        { label: 'Assistant IA & Inférence', icon: Bot, action: () => { router.push('/dashboard/predictions'); onClose(); } },
        { label: 'Facturation & Gain-Share', icon: Receipt, action: () => { router.push('/dashboard/facturation'); onClose(); } },
        { label: 'Supervision Multi-Sites', icon: Factory, action: () => { router.push('/dashboard/sites'); onClose(); } },
        { label: 'Console Administrateur MLOps', icon: Settings, action: () => { router.push('/dashboard/admin'); onClose(); } },
      ],
    },
    {
      category: 'Niveaux Cognitifs',
      items: [
        { label: 'Basculer en mode Débutant (Ménage)', icon: ShieldCheck, action: () => { if (onSelectLevel) onSelectLevel('debutant'); onClose(); } },
        { label: 'Basculer en mode Amateur (PME)', icon: Leaf, action: () => { if (onSelectLevel) onSelectLevel('amateur'); onClose(); } },
        { label: 'Basculer en mode Technique (Industrie)', icon: AlertTriangle, action: () => { if (onSelectLevel) onSelectLevel('technique'); onClose(); } },
      ],
    },
  ];

  const filteredActions = actions.map((group) => ({
    ...group,
    items: group.items.filter((item) =>
      item.label.toLowerCase().includes(query.toLowerCase())
    ),
  })).filter((group) => group.items.length > 0);

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(4px)',
        zIndex: 99990,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '15vh',
        paddingLeft: '16px',
        paddingRight: '16px',
      }}
      onClick={onClose}
    >
      <div
        className="card-standard"
        style={{
          width: '100%',
          maxWidth: '580px',
          padding: 0,
          backgroundColor: 'var(--bg-elevated)',
          boxShadow: 'var(--shadow-dropdown)',
          overflow: 'hidden',
          borderRadius: 'var(--radius-lg)',
          animation: 'fadeIn 0.15s ease-out forwards',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Barre de recherche */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '16px 20px',
            borderBottom: '1px solid var(--border-color)',
          }}
        >
          <Search size={18} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Rechercher une page, une action ou un niveau (Ctrl+K)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            style={{
              width: '100%',
              border: 'none',
              outline: 'none',
              background: 'transparent',
              fontSize: '15px',
              color: 'var(--text-primary)',
              fontFamily: 'inherit',
            }}
          />
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Liste des commandes */}
        <div style={{ maxHeight: '340px', overflowY: 'auto', padding: '8px' }}>
          {filteredActions.map((group) => (
            <div key={group.category} style={{ marginBottom: '12px' }}>
              <div
                style={{
                  fontSize: '10px',
                  fontWeight: 800,
                  color: 'var(--text-muted)',
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  padding: '6px 12px',
                }}
              >
                {group.category}
              </div>
              {group.items.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <button
                    key={idx}
                    onClick={item.action}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      width: '100%',
                      padding: '10px 12px',
                      border: 'none',
                      borderRadius: 'var(--radius-sm)',
                      background: 'transparent',
                      color: 'var(--text-primary)',
                      fontSize: '14px',
                      fontWeight: 500,
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'background-color 0.1s ease',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-surface)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <Icon size={16} color="var(--accent-cta)" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          ))}

          {filteredActions.length === 0 && (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
              Aucun résultat correspondant à "{query}".
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: '10px 16px',
            backgroundColor: 'var(--bg-surface)',
            borderTop: '1px solid var(--border-color)',
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '11px',
            color: 'var(--text-muted)',
          }}
        >
          <span>Astuce : Utilisez <kbd style={{ padding: '2px 5px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '3px' }}>Échap</kbd> pour fermer</span>
          <span>NouanKanyAI Command v2.0</span>
        </div>
      </div>
    </div>
  );
}
