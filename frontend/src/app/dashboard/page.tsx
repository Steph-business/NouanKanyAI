'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowUpRight, Zap, Target, Power, AlertTriangle, Bot, Leaf } from 'lucide-react';
import { BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { supabase } from '@/lib/supabase';
import { API_URL } from '@/lib/api';

// Génère un profil de consommation journalier réaliste à partir de la puissance totale des machines
function generateDailyProfile(totalKw: number) {
  const profile = [
    { time: '00h', factor: 0.3 },
    { time: '04h', factor: 0.2 },
    { time: '08h', factor: 0.75 },
    { time: '10h', factor: 1.0 },
    { time: '12h', factor: 0.9 },
    { time: '14h', factor: 1.0 },
    { time: '16h', factor: 0.95 },
    { time: '18h', factor: 0.85 },
    { time: '20h', factor: 0.65 },
    { time: '22h', factor: 0.45 },
  ];
  return profile.map(p => ({
    time: p.time,
    conso: parseFloat((totalKw * p.factor * (0.9 + Math.random() * 0.2)).toFixed(1))
  }));
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  
  // États pour les appareils venant de l'API
  const [machines, setMachines] = useState<any[]>([]);
  const [totalConso, setTotalConso] = useState(0);
  const [aiSuggestion, setAiSuggestion] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [economiesMois, setEconomiesMois] = useState(0);

  // États pour les notifications (Toast) et le chargement
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState<'info' | 'error' | 'success'>('info');
  const [loadingMachineId, setLoadingMachineId] = useState<string | null>(null);

  const showToast = (msg: string, type: 'info' | 'error' | 'success' = 'info') => {
    setToastMessage(msg);
    setToastType(type);
    setTimeout(() => setToastMessage(''), 3500);
  };

  useEffect(() => {
    const checkUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session && session.user) {
        setUser({
          nom: session.user.user_metadata?.nom || session.user.email,
          email: session.user.email
        });
      } else {
        router.push('/');
      }
    };
    checkUser();
    
    // Fetch live machines state
    const fetchMachines = async () => {
      try {
        const res = await fetch(`${API_URL}/api/machines`);
        const data = await res.json();
        setMachines(data);
        
        // Calculate total consumption dynamically
        const total = data.reduce((acc: number, m: any) => acc + (['actif', 'eco'].includes(m.status) ? m.power_kw : 0), 0);
        setTotalConso(total);
        
        // Generate realistic chart data from real machine power
        setChartData(generateDailyProfile(total));
        
        // Calculate monthly savings dynamically: 15% savings at CIE tariff 68 FCFA/kWh
        const monthlySavings = total * 24 * 30 * 68 * 0.15;
        setEconomiesMois(monthlySavings);

        // Fetch AI recommendation
        if (data.length > 0) {
          const recRes = await fetch(`${API_URL}/api/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state: data })
          });
          const recData = await recRes.json();
          if (recData.recommendations && recData.recommendations.length > 0) {
            setAiSuggestion(recData.recommendations[0]);
          } else {
            setAiSuggestion(null);
          }
        }
      } catch (err) {
        console.error("Failed to fetch machines/recommendations:", err);
      }
    };
    
    fetchMachines();
    const interval = setInterval(fetchMachines, 5000);
    return () => clearInterval(interval);
  }, []);

  const toggleAppareil = async (machine_id: string, nom: string, current_status: string) => {
    if (loadingMachineId) return; // Prevent double clicks
    
    setLoadingMachineId(machine_id);
    const actionText = ['actif', 'eco'].includes(current_status) ? `Mise hors tension de ${nom}...` : `Allumage de ${nom}...`;
    const actionType = ['actif', 'eco'].includes(current_status) ? 'info' : 'success';
    
    showToast(actionText, actionType);

    try {
      await fetch(`http://localhost:8000/api/machines/${machine_id}/toggle`, { method: 'POST' });
      // Fetch machines again to update UI
      const res = await fetch('http://localhost:8000/api/machines');
      const data = await res.json();
      setMachines(data);
      const total = data.reduce((acc: number, m: any) => acc + (['actif', 'eco'].includes(m.status) ? m.power_kw : 0), 0);
      setTotalConso(total);
      
      showToast(['actif', 'eco'].includes(current_status) ? `${nom} est maintenant hors ligne.` : `${nom} est maintenant actif.`, 'success');
    } catch (err) {
      console.error("Erreur lors du basculement", err);
      showToast("Erreur lors de la modification du statut.", 'error');
    } finally {
      setLoadingMachineId(null);
    }
  };

  const toggleEco = async (machine_id: string, nom: string) => {
    if (loadingMachineId) return;
    setLoadingMachineId(machine_id);
    showToast(`Activation du mode Éco sur ${nom}...`, 'info');
    
    try {
      await fetch(`http://localhost:8000/api/machines/${machine_id}/eco`, { method: 'POST' });
      const res = await fetch('http://localhost:8000/api/machines');
      const data = await res.json();
      setMachines(data);
      const total = data.reduce((acc: number, m: any) => acc + (['actif', 'eco'].includes(m.status) ? m.power_kw : 0), 0);
      setTotalConso(total);
      showToast(`Mode Éco activé pour ${nom} (-35% de conso).`, 'success');
    } catch (err) {
      console.error("Erreur lors du mode éco", err);
      showToast("Erreur lors de l'activation du mode Éco.", 'error');
    } finally {
      setLoadingMachineId(null);
    }
  };

  if (!user) return null;


  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '32px', fontWeight: 800, marginBottom: '6px' }}>
            Bonjour, {user.nom.split(' ')[0]} 👋
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
            Voici la vue d'ensemble de votre infrastructure énergétique.
          </p>
        </div>
      </div>

      {/* Alerte IA Premium Banner */}
      {aiSuggestion && (
        <div style={{ 
          display: 'flex', 
          alignItems: 'flex-start', 
          gap: '16px', 
          padding: '20px', 
          background: aiSuggestion.type.includes('Surchauffe') 
            ? 'linear-gradient(135deg, rgba(220, 38, 38, 0.08) 0%, rgba(220, 38, 38, 0.02) 100%)' 
            : 'linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(245, 158, 11, 0.02) 100%)',
          border: `1px solid ${aiSuggestion.type.includes('Surchauffe') ? 'rgba(220, 62, 62, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`, 
          borderLeft: `4px solid ${aiSuggestion.type.includes('Surchauffe') ? '#ef4444' : 'var(--accent)'}`,
          borderRadius: '12px', 
          marginBottom: '32px',
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.25)',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{ 
            backgroundColor: aiSuggestion.type.includes('Surchauffe') ? 'var(--danger)' : 'var(--accent)', 
            padding: '8px', 
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 0 15px ${aiSuggestion.type.includes('Surchauffe') ? 'rgba(239, 68, 68, 0.4)' : 'rgba(245, 158, 11, 0.4)'}`
          }}>
            {aiSuggestion.type.includes('Surchauffe') ? <AlertTriangle size={18} color="#fff" /> : <Bot size={18} color="#fff" />}
          </div>
          <div>
            <div style={{ 
              fontWeight: 700, 
              color: aiSuggestion.type.includes('Surchauffe') ? '#f87171' : 'var(--accent)', 
              marginBottom: '6px', 
              fontSize: '15px',
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px' 
            }}>
              {aiSuggestion.type} sur {aiSuggestion.machine_id}
            </div>
            <div style={{ color: 'var(--text-subtle)', fontSize: '14px', lineHeight: '1.5' }}>
              {aiSuggestion.action}
            </div>
          </div>
        </div>
      )}

      <div className="kpi-grid">
        {/* KPI 1 : Conso */}
        <div className="glass-card glow-card-cyan">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Consommation (Aujourd'hui)</div>
            <div style={{ backgroundColor: 'rgba(6, 182, 212, 0.1)', padding: '8px', borderRadius: '8px', border: '1px solid rgba(6, 182, 212, 0.15)' }}>
              <Zap size={16} color="var(--secondary)" />
            </div>
          </div>
          <div style={{ fontSize: '32px', fontFamily: 'Outfit, sans-serif', fontWeight: 800, marginBottom: '8px', color: 'var(--foreground)' }}>
            {totalConso.toFixed(1)} <span style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: 600 }}>kW</span>
          </div>
          <div style={{ color: 'var(--primary)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 700 }}>
            <ArrowUpRight size={14} /> -12% depuis hier
          </div>
        </div>

        {/* KPI 2 : Économies */}
        <div className="glass-card glow-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Économies Générées (Mois)</div>
            <div style={{ backgroundColor: 'var(--primary-light)', padding: '8px', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              <Target size={16} color="var(--primary)" />
            </div>
          </div>
          <div style={{ fontSize: '32px', fontFamily: 'Outfit, sans-serif', fontWeight: 800, marginBottom: '8px', color: 'var(--foreground)' }}>
            {economiesMois > 0
              ? `${(economiesMois / 1_000_000).toFixed(1)}M`
              : '—'
            } <span style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: 600 }}>XOF</span>
          </div>
          <div style={{ color: 'var(--primary)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 700 }}>
            <ArrowUpRight size={14} /> +12.4% d'optimisation IA
          </div>
        </div>
      </div>

      <div className="grid-2-1">
        {/* Graphique */}
        <div className="glass-card" style={{ height: '380px', padding: '28px' }}>
          <h3 style={{ marginBottom: '24px', fontWeight: 700, fontSize: '16px', color: 'var(--foreground)' }}>Évolution de la consommation</h3>
          <div style={{ width: '100%', height: 'calc(100% - 40px)' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="consoActive" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--secondary)" stopOpacity={1}/>
                    <stop offset="100%" stopColor="var(--secondary)" stopOpacity={0.3}/>
                  </linearGradient>
                  <linearGradient id="consoDim" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="rgba(255,255,255,0.15)" stopOpacity={1}/>
                    <stop offset="100%" stopColor="rgba(255,255,255,0.02)" stopOpacity={0.3}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip 
                  cursor={{fill: 'var(--surface-hover)'}}
                  contentStyle={{ backgroundColor: 'var(--background-alt)', borderColor: 'var(--surface-border)', borderRadius: '8px' }}
                  itemStyle={{ color: 'var(--foreground)', fontSize: '13px' }}
                  labelStyle={{ color: 'var(--text-muted)', fontSize: '12px', fontWeight: 600 }}
                />
                <Bar dataKey="conso" radius={[4, 4, 0, 0]}>
                   {chartData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={entry.conso > (totalConso * 0.8) ? 'url(#consoActive)' : 'url(#consoDim)'} 
                      />
                    ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Contrôle des Appareils Favoris */}
        <div className="glass-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <h3 style={{ fontWeight: 700, fontSize: '16px', color: 'var(--foreground)' }}>Appareils Énergivores</h3>
            <span onClick={() => router.push('/dashboard/appareils')} style={{ fontSize: '11px', color: 'var(--primary)', fontWeight: 700, letterSpacing: '0.05em', cursor: 'pointer' }}>VOIR TOUT</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {machines.slice(0, 3).map((appareil) => (
              <div key={appareil.machine_id} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                padding: '16px', 
                border: '1px solid var(--surface-border)', 
                borderRadius: '12px',
                backgroundColor: 'rgba(255, 255, 255, 0.01)',
                transition: 'all 0.2s ease'
              }}
              className="nav-item-hover-only" // Added simple border hover
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px', color: 'var(--foreground)' }}>{appareil.nom}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{appareil.power_kw} kW • {appareil.temperature_c.toFixed(1)}°C</div>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <div 
                    onClick={() => toggleEco(appareil.machine_id, appareil.nom)}
                    style={{ 
                      cursor: loadingMachineId === appareil.machine_id ? 'wait' : 'pointer', 
                      padding: '8px', 
                      borderRadius: '50%', 
                      backgroundColor: appareil.status === 'eco' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                      color: appareil.status === 'eco' ? '#10b981' : 'var(--text-muted)',
                      border: appareil.status === 'eco' ? '1px solid #10b981' : '1px solid var(--surface-border)',
                      transition: 'all 0.2s',
                      opacity: loadingMachineId === appareil.machine_id ? 0.5 : 1,
                      transform: loadingMachineId === appareil.machine_id ? 'scale(0.95)' : 'scale(1)'
                    }}
                    title="Mode Éco (Réguler la consommation)"
                  >
                    <Leaf size={16} />
                  </div>
                  <div 
                    onClick={() => toggleAppareil(appareil.machine_id, appareil.nom, appareil.status)}
                    style={{ 
                      cursor: loadingMachineId === appareil.machine_id ? 'wait' : 'pointer', 
                      padding: '8px', 
                      borderRadius: '50%', 
                      backgroundColor: ['actif', 'eco'].includes(appareil.status) ? 'var(--primary-light)' : 'rgba(239, 68, 68, 0.1)',
                      color: ['actif', 'eco'].includes(appareil.status) ? 'var(--primary)' : '#EF4444',
                      border: ['actif', 'eco'].includes(appareil.status) ? '1px solid rgba(16, 185, 129, 0.25)' : '1px solid rgba(239, 68, 68, 0.2)',
                      transition: 'all 0.2s',
                      opacity: loadingMachineId === appareil.machine_id ? 0.5 : 1,
                      transform: loadingMachineId === appareil.machine_id ? 'scale(0.95)' : 'scale(1)'
                    }}
                  >
                    <Power size={16} className={loadingMachineId === appareil.machine_id ? "spin-animation" : ""} />
                  </div>
                </div>
              </div>
            ))}
            {machines.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px', padding: '24px' }}>
                Aucune machine enregistrée.
              </div>
            )}
          </div>
        </div>
      </div>
      {/* Custom Toast Notification pour le Dashboard */}
      {toastMessage && (
        <div style={{ 
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
          animation: 'fadeInUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
        }}>
          <span style={{ fontSize: '18px' }}>{toastType === 'error' ? '⚠' : toastType === 'success' ? '✓' : 'ℹ'}</span>
          {toastMessage}
        </div>
      )}

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes spinPulse {
          0% { transform: rotate(0deg) scale(1); }
          50% { transform: rotate(180deg) scale(0.8); }
          100% { transform: rotate(360deg) scale(1); }
        }
        .spin-animation {
          animation: spinPulse 1s linear infinite;
        }
      `}} />
    </div>
  );
}
