'use client';

import React, { useEffect } from 'react';
import { CheckCircle2, AlertTriangle, AlertOctagon, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastMessage {
  id: string;
  message: string;
  type?: ToastType;
  duration?: number;
}

interface ToastProps {
  toast: ToastMessage | null;
  onClose: () => void;
}

/**
 * Toast — Système de notifications ultra-propre et accessible.
 */
export function Toast({ toast, onClose }: ToastProps) {
  useEffect(() => {
    if (!toast) return;
    const duration = toast.duration || 3500;
    const timer = setTimeout(() => {
      onClose();
    }, duration);
    return () => clearTimeout(timer);
  }, [toast, onClose]);

  if (!toast) return null;

  const typeConfigs = {
    success: {
      bg: 'var(--status-success)',
      color: '#FFFFFF',
      icon: CheckCircle2,
      border: 'var(--status-success-border)',
    },
    error: {
      bg: 'var(--status-alert)',
      color: '#FFFFFF',
      icon: AlertOctagon,
      border: 'var(--status-alert-border)',
    },
    warning: {
      bg: 'var(--status-warning)',
      color: '#FFFFFF',
      icon: AlertTriangle,
      border: 'var(--status-warning-border)',
    },
    info: {
      bg: 'var(--text-primary)',
      color: '#FFFFFF',
      icon: Info,
      border: 'var(--border-color)',
    },
  };

  const config = typeConfigs[toast.type || 'info'];
  const Icon = config.icon;

  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        zIndex: 99999,
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '14px 20px',
        borderRadius: 'var(--radius-md)',
        backgroundColor: config.bg,
        color: config.color,
        boxShadow: 'var(--shadow-dropdown)',
        maxWidth: '420px',
        animation: 'fadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards',
      }}
    >
      <Icon size={18} style={{ flexShrink: 0 }} />
      <span style={{ fontSize: '14px', fontWeight: 600, flex: 1, lineHeight: 1.4 }}>
        {toast.message}
      </span>
      <button
        onClick={onClose}
        style={{
          background: 'none',
          border: 'none',
          color: 'inherit',
          opacity: 0.8,
          cursor: 'pointer',
          padding: '2px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        aria-label="Fermer la notification"
      >
        <X size={16} />
      </button>
    </div>
  );
}
