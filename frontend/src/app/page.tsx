'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { supabase } from '@/lib/supabase';

export default function Home() {
  const router = useRouter();
  
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  
  const [nom, setNom] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [typeCompte, setTypeCompte] = useState('Industriel');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toastMessage, setToastMessage] = useState('');

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 3500);
  };

  useEffect(() => {
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      const mockUser = localStorage.getItem('mockUser');
      if (session || mockUser) {
        router.push('/dashboard');
      }
    };
    checkSession();
  }, [router]);

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Mock login bypass for demo
    const mockUser = {
      nom: nom || email.split('@')[0],
      email: email,
      type_compte: typeCompte
    };
    localStorage.setItem('mockUser', JSON.stringify(mockUser));
    
    showToast("Connexion réussie ! Redirection en cours...");
    setTimeout(() => {
      router.push('/dashboard');
    }, 1200);
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--background)' }}>
      {/* Left Column - Value Prop */}
      <div style={{ flex: 1, padding: '60px 8%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '40px' }}>
          <Image 
            src="/NouankanyAI.png" 
            alt="NouanKanyAI Logo" 
            width={48} 
            height={48} 
            style={{ objectFit: 'contain' }} 
            priority
          />
          <span style={{ fontSize: '28px', fontWeight: 800, fontFamily: 'Outfit, sans-serif', color: 'var(--foreground)', letterSpacing: '-0.02em' }}>
            NouankanyAI
          </span>
        </div>
        
        <h1 style={{ fontSize: '56px', fontWeight: 800, color: 'var(--foreground)', lineHeight: 1.1, marginBottom: '24px', letterSpacing: '-0.03em' }}>
          L'intelligence au service de votre <span style={{ color: 'var(--primary)' }}>énergie</span>.
        </h1>
        <p style={{ fontSize: '18px', color: 'var(--text-subtle)', lineHeight: 1.6, marginBottom: '40px', maxWidth: '540px' }}>
          Reprenez le contrôle de vos installations industrielles. 
          Analysez vos données avec une précision inégalée, identifiez les gaspillages 
          et laissez notre IA optimiser vos équipements en temps réel.
        </p>
        
        <div style={{ display: 'flex', gap: '24px', color: 'var(--text-muted)', fontSize: '14px', fontWeight: 500 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--primary)' }}></div>
            Réduction des coûts
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--secondary)' }}></div>
            Automatisation intelligente
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent)' }}></div>
            Bilan carbone optimisé
          </div>
        </div>
      </div>

      {/* Right Column - Auth Form */}
      <div style={{ width: '500px', backgroundColor: 'var(--surface)', borderLeft: '1px solid var(--surface-border)', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '60px' }}>
        <h3 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '8px', color: 'var(--foreground)' }}>
          {authMode === 'login' ? 'Bon retour parmi nous' : 'Créer un espace industriel'}
        </h3>
        <p style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '32px' }}>
          {authMode === 'login' 
            ? 'Connectez-vous pour accéder à votre tableau de bord.' 
            : 'Rejoignez le réseau NouanKanyAI.'}
        </p>

        <form onSubmit={handleAuthSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {authMode === 'register' && (
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-subtle)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Nom complet</label>
              <input 
                type="text" 
                placeholder="Ex: Entreprise SA" 
                value={nom}
                onChange={(e) => setNom(e.target.value)}
                style={{ width: '100%', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--surface-border)', backgroundColor: 'var(--background)', color: 'var(--foreground)', fontSize: '14px', outline: 'none', transition: 'border-color 0.2s' }}
                onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
                onBlur={(e) => e.target.style.borderColor = 'var(--surface-border)'}
                required
              />
            </div>
          )}
          
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-subtle)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Adresse Email</label>
            <input 
              type="email" 
              placeholder="vous@entreprise.com" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ width: '100%', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--surface-border)', backgroundColor: 'var(--background)', color: 'var(--foreground)', fontSize: '14px', outline: 'none', transition: 'border-color 0.2s' }}
              onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--surface-border)'}
              required
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-subtle)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Mot de passe</label>
            <input 
              type="password" 
              placeholder="••••••••" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: '100%', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--surface-border)', backgroundColor: 'var(--background)', color: 'var(--foreground)', fontSize: '14px', outline: 'none', transition: 'border-color 0.2s' }}
              onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--surface-border)'}
              required
            />
          </div>

          {authMode === 'register' && (
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-subtle)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Type de compte</label>
              <select 
                value={typeCompte}
                onChange={(e) => setTypeCompte(e.target.value)}
                style={{ width: '100%', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--surface-border)', backgroundColor: 'var(--background)', color: 'var(--foreground)', fontSize: '14px', outline: 'none', cursor: 'pointer' }}
              >
                <option value="Industriel">Industriel</option>
                <option value="Entreprise">Entreprise</option>
                <option value="Particulier">Particulier</option>
              </select>
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading}
            style={{ width: '100%', padding: '14px', backgroundColor: 'var(--primary)', color: '#ffffff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer', marginTop: '12px', transition: 'background-color 0.2s', boxShadow: '0 4px 6px -1px var(--primary-dim)' }}
            onMouseEnter={(e) => { if(!loading) e.currentTarget.style.backgroundColor = 'var(--primary-hover)' }}
            onMouseLeave={(e) => { if(!loading) e.currentTarget.style.backgroundColor = 'var(--primary)' }}
          >
            {loading ? 'Connexion en cours...' : (authMode === 'login' ? 'Accéder au panneau de contrôle' : 'Créer mon espace')}
          </button>
        </form>

        <div style={{ marginTop: '32px', textAlign: 'center' }}>
          <button 
            onClick={() => {
              setAuthMode(authMode === 'login' ? 'register' : 'login');
              setError('');
            }}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '14px', fontWeight: 500, cursor: 'pointer', textDecoration: 'underline' }}
          >
            {authMode === 'login' ? "Je n'ai pas de compte. S'inscrire" : "J'ai déjà un compte. Se connecter"}
          </button>
        </div>
      </div>

      {toastMessage && (
        <div style={{ 
          position: 'fixed', bottom: '32px', right: '32px', 
          backgroundColor: 'var(--primary)', color: '#fff', padding: '16px 24px', 
          borderRadius: '12px', fontWeight: 600, zIndex: 99999, 
          boxShadow: '0 10px 30px var(--primary-dim)',
          display: 'flex', alignItems: 'center', gap: '12px',
          animation: 'fadeInUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
        }}>
          <span>✓</span>
          {toastMessage}
        </div>
      )}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}} />
    </div>
  );
}

