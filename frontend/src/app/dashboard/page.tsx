'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Zap,
  TrendingUp,
  ShieldCheck,
  AlertTriangle,
  Leaf,
  Power,
  RotateCcw,
  ArrowRight,
  ArrowUpRight,
  Bot,
  Activity,
  Calculator,
  UploadCloud,
  Layers,
  Sparkles,
} from 'lucide-react';
import { BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { API_URL } from '@/lib/api';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';
import { AlertCard } from '@/components/ui/AlertCard';
import { CieTariffBar } from '@/components/ui/CieTariffBar';
import { InvoiceUploadWidget } from '@/components/ui/InvoiceUploadWidget';
import { MediaAnalyzerWidget } from '@/components/ui/MediaAnalyzerWidget';
import { Toast, ToastMessage } from '@/components/ui/Toast';
import { UserLevel } from '@/components/ui/LevelSelector';

// Profil de consommation journalier réaliste
function generateDailyProfile(totalKw: number) {
  const profile = [
    { time: '00h', factor: 0.3 },
    { time: '04h', factor: 0.25 },
    { time: '08h', factor: 0.75 },
    { time: '10h', factor: 0.95 },
    { time: '12h', factor: 0.9 },
    { time: '14h', factor: 1.0 },
    { time: '16h', factor: 0.92 },
    { time: '18h', factor: 0.85 },
    { time: '20h', factor: 0.65 },
    { time: '22h', factor: 0.45 },
  ];
  return profile.map((p) => ({
    time: p.time,
    conso: parseFloat((totalKw * p.factor * (0.92 + Math.random() * 0.16)).toFixed(1)),
  }));
}

export default function DashboardOverviewPage() {
  const router = useRouter();

  const [user, setUser] = useState<any>(null);
  const [machines, setMachines] = useState<any[]>([]);
  const [totalConso, setTotalConso] = useState(0);
  const [aiSuggestion, setAiSuggestion] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [economiesMois, setEconomiesMois] = useState(0);
  const [loadingMachineId, setLoadingMachineId] = useState<string | null>(null);

  // Profil et Niveau d'expertise
  const [activeProfile, setActiveProfile] = useState<string>('PME');
  const [currentLevel, setCurrentLevel] = useState<UserLevel>('amateur');

  // Auto-executed logs
  const [autoExecutedLogs, setAutoExecutedLogs] = useState<Array<{ id: string; title: string; time: string; machineId: string }>>([
    { id: '1', title: 'Délestage préventif appliqué', machineId: 'COMP-02', time: 'Il y a 25 min' },
  ]);

  // Toast
  const [toast, setToast] = useState<ToastMessage | null>(null);

  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    setToast({ id: Date.now().toString(), message, type });
  };

  useEffect(() => {
    const savedProfile = localStorage.getItem('nouankanyai_profile') || 'PME';
    setActiveProfile(savedProfile);

    const savedLevel = (localStorage.getItem('nouankanyai_level') as UserLevel) || 'amateur';
    setCurrentLevel(savedLevel);

    const mockUser = localStorage.getItem('mockUser');
    if (mockUser) {
      setUser(JSON.parse(mockUser));
    } else {
      setUser({ nom: 'Responsable Énergie', email: 'contact@nouankanyai.ci' });
    }

    const fetchMachines = async () => {
      try {
        const res = await fetch(`${API_URL}/api/machines`);
        const data = await res.json();
        setMachines(data);

        const total = data.reduce(
          (acc: number, m: any) => acc + (['actif', 'eco'].includes(m.status) ? m.power_kw : 0),
          0
        );
        setTotalConso(total);
        setChartData(generateDailyProfile(total || 65));

        // Économies mensuelles estimées à 15% au tarif CIE
        const monthlySavings = (total || 65) * 24 * 30 * 68 * 0.15;
        setEconomiesMois(monthlySavings);

        // Fetch AI suggestions
        if (data.length > 0) {
          const recRes = await fetch(`${API_URL}/api/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state: data }),
          });
          const recData = await recRes.json();
          if (recData.recommendations && recData.recommendations.length > 0) {
            setAiSuggestion(recData.recommendations[0]);
          }
        }
      } catch (err) {
        console.error("Erreur chargement machines :", err);
      }
    };

    fetchMachines();
    const interval = setInterval(fetchMachines, 6000);
    return () => clearInterval(interval);
  }, []);

  // Actions physiques sur les machines
  const toggleAppareil = async (machine_id: string, nom: string, current_status: string) => {
    if (loadingMachineId) return;
    setLoadingMachineId(machine_id);

    try {
      await fetch(`${API_URL}/api/machines/${machine_id}/toggle`, { method: 'POST' });
      const res = await fetch(`${API_URL}/api/machines`);
      const data = await res.json();
      setMachines(data);

      const total = data.reduce(
        (acc: number, m: any) => acc + (['actif', 'eco'].includes(m.status) ? m.power_kw : 0),
        0
      );
      setTotalConso(total);

      const isOff = ['actif', 'eco'].includes(current_status);
      showToast(isOff ? `${nom} mis hors tension avec succès.` : `${nom} réactivé.`, 'success');
    } catch (err) {
      showToast("Erreur lors du basculement d'alimentation.", 'error');
    } finally {
      setLoadingMachineId(null);
    }
  };

  const toggleEco = async (machine_id: string, nom: string) => {
    if (loadingMachineId) return;
    setLoadingMachineId(machine_id);

    try {
      await fetch(`${API_URL}/api/machines/${machine_id}/eco`, { method: 'POST' });
      const res = await fetch(`${API_URL}/api/machines`);
      const data = await res.json();
      setMachines(data);

      const total = data.reduce(
        (acc: number, m: any) => acc + (['actif', 'eco'].includes(m.status) ? m.power_kw : 0),
        0
      );
      setTotalConso(total);

      // Ajouter à l'historique des actions auto-exécutées
      setAutoExecutedLogs((prev) => [
        { id: Date.now().toString(), title: `Mode Éco activé (-35% puissance)`, machineId: machine_id, time: 'À l\'instant' },
        ...prev,
      ]);

      showToast(`Mode Éco activé sur ${nom} (-35% de puissance).`, 'success');
    } catch (err) {
      showToast("Erreur lors de l'activation du mode Éco.", 'error');
    } finally {
      setLoadingMachineId(null);
    }
  };

  if (!user) return null;

  return (
    <div>
      {/* En-tête de bienvenue avec badge de profil */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cta)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Espace {activeProfile}
            </span>
            <ProvenanceBadge type="mesure" label="Réseau CIE Actif" />
          </div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
            Bonjour, {user.nom?.split(' ')[0] || 'Responsable'} 👋
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
            Supervision de vos index énergétiques et pilotage intelligent en temps réel.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button
            onClick={() => router.push('/dashboard/predictions')}
            className="btn-outline"
            style={{ fontSize: '12px', padding: '8px 14px' }}
          >
            <Bot size={15} color="var(--accent-cta)" />
            <span>Copilot IA</span>
          </button>
        </div>
      </div>

      {/* =====================================================================
          HIÉRARCHIE 1 : ALERTE ACTIVE VISUELLEMENT DOMINANTE (Non négociable)
          Différenciation stricte Action requise vs Auto-exécutée
      ===================================================================== */}
      {aiSuggestion && (
        <AlertCard
          register="action_requise"
          title={aiSuggestion.type || "Alerte de Surcharge Détectée"}
          machineId={aiSuggestion.machine_id}
          description={aiSuggestion.action || "La puissance appelée approche le palier tarifaire supérieur CIE. Une réduction immédiate de charge est recommandée."}
          actionText="Exécuter la régulation immédiate"
          onActionClick={() => toggleEco(aiSuggestion.machine_id, aiSuggestion.machine_id)}
          gainFcfa={aiSuggestion.gain_fcfa || 8500}
          severity={aiSuggestion.type?.includes('Surchauffe') ? 'critique' : 'moderee'}
          timestamp="Alerte active • Détectée il y a 3 min"
          provenance="synthetique"
          loading={loadingMachineId === aiSuggestion.machine_id}
        />
      )}

      {/* Actions auto-exécutées journalisées */}
      {autoExecutedLogs.length > 0 && (
        <AlertCard
          register="auto_executee"
          title={autoExecutedLogs[0].title}
          machineId={autoExecutedLogs[0].machineId}
          description="Régulation de puissance appliquée automatiquement selon les règles de pilotage préventif sans interruption de service."
          timestamp={autoExecutedLogs[0].time}
          provenance="synthetique"
          actionText="Voir l'historique"
          onActionClick={() => router.push('/dashboard/predictions')}
        />
      )}

      {/* =====================================================================
          HIÉRARCHIE 2 : KPIS DE CONSOMMATION & COÛTS (Tabular numbers)
      ===================================================================== */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '18px', marginBottom: '28px' }}>
        {/* KPI 1 : Puissance active */}
        <div className="card-standard" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Puissance Active Instantanée
            </span>
            <ProvenanceBadge type="mesure" label="Index" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '6px' }}>
            <span
              className="tabular-numbers"
              style={{
                fontSize: '32px',
                fontWeight: 800,
                color: 'var(--text-primary)',
                fontFamily: 'IBM Plex Mono, monospace',
              }}
            >
              {totalConso.toFixed(1)}
            </span>
            <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-secondary)' }}>
              kW
            </span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--status-success)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
            <ArrowUpRight size={14} /> -12.4% vs consommation de référence
          </div>
        </div>

        {/* KPI 2 : Économies générées */}
        <div className="card-standard" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Économies Réalisées (Ce Mois)
            </span>
            <ProvenanceBadge type="estime" label="CIE 68 F" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '6px' }}>
            <span
              className="tabular-numbers"
              style={{
                fontSize: '32px',
                fontWeight: 800,
                color: 'var(--status-success)',
                fontFamily: 'IBM Plex Mono, monospace',
              }}
            >
              {economiesMois.toLocaleString('fr-FR', { maximumFractionDigits: 0 })}
            </span>
            <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--status-success)' }}>
              FCFA
            </span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Modèle Gain-Share : 90% client ({(economiesMois * 0.9).toLocaleString('fr-FR', { maximumFractionDigits: 0 })} FCFA)
          </div>
        </div>

        {/* KPI 3 : Palier tarifaire actuel */}
        <div className="card-standard" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Palier Tarifaire CIE
            </span>
            <ProvenanceBadge type="mesure" label="Tranche" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '6px' }}>
            <span
              style={{
                fontSize: '24px',
                fontWeight: 800,
                color: 'var(--accent-cost)',
                fontFamily: 'Space Grotesk, sans-serif',
              }}
            >
              Non Domestique
            </span>
          </div>
          <div className="tabular-numbers" style={{ fontSize: '12px', color: 'var(--text-secondary)', fontFamily: 'IBM Plex Mono, monospace' }}>
            Tarif unitaire : <strong>68 FCFA / kWh</strong> (151 – 500 kWh)
          </div>
        </div>
      </div>

      {/* Grille principale : Graphique de Charge & Équipements Clés */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '28px' }} className="grid-responsive-2-1">
        {/* Courbe de Charge Journalière */}
        <div className="card-standard" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '8px' }}>
            <div>
              <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                Courbe de Charge Journalière (24h)
              </h3>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
                Profil horaire actualisé selon l'état des machines en service
              </p>
            </div>
            <ProvenanceBadge type="synthetique" label="Profil Calibré" />
          </div>

          <div style={{ height: '240px', width: '100%', flex: 1 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  cursor={{ fill: 'var(--bg-surface)' }}
                  contentStyle={{
                    backgroundColor: 'var(--bg-elevated)',
                    borderColor: 'var(--border-color)',
                    borderRadius: 'var(--radius-sm)',
                    boxShadow: 'var(--shadow-md)',
                  }}
                  itemStyle={{ color: 'var(--text-primary)', fontSize: '13px', fontWeight: 600 }}
                  labelStyle={{ color: 'var(--text-secondary)', fontSize: '11px', fontWeight: 700 }}
                  formatter={(value: any) => [`${value} kW`, 'Puissance']}
                />
                <Bar dataKey="conso" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.conso > totalConso * 0.85 ? 'var(--accent-cta)' : 'var(--border-strong)'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Contrôle des Machines / Équipements */}
        <div className="card-standard" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
              Équipements Clés
            </h3>
            <button
              onClick={() => router.push('/dashboard/appareils')}
              className="btn-ghost"
              style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-cta)' }}
            >
              VOIR TOUT ({machines.length})
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1, overflowY: 'auto' }}>
            {machines.slice(0, 4).map((appareil) => {
              const isEco = appareil.status === 'eco';
              const isActive = ['actif', 'eco'].includes(appareil.status);
              const isAlert = appareil.status === 'alerte';

              return (
                <div
                  key={appareil.machine_id}
                  style={{
                    padding: '14px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: isAlert ? 'var(--status-alert-bg)' : 'var(--bg-surface)',
                    border: `1px solid ${isAlert ? 'var(--status-alert-border)' : 'var(--border-color)'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span
                        style={{
                          width: '7px',
                          height: '7px',
                          borderRadius: '50%',
                          backgroundColor: isAlert ? 'var(--status-alert)' : isEco ? 'var(--status-warning)' : isActive ? 'var(--status-success)' : 'var(--text-muted)',
                        }}
                      />
                      <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-primary)' }}>
                        {appareil.nom}
                      </span>
                    </div>
                    <div className="tabular-numbers" style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px', fontFamily: 'IBM Plex Mono, monospace' }}>
                      {appareil.power_kw} kW • {appareil.temperature_c?.toFixed(1)}°C
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button
                      onClick={() => toggleEco(appareil.machine_id, appareil.nom)}
                      title="Mode Éco (-35% de charge)"
                      disabled={loadingMachineId === appareil.machine_id}
                      style={{
                        padding: '6px 10px',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: isEco ? 'var(--status-success-bg)' : 'var(--bg-card)',
                        color: isEco ? 'var(--status-success)' : 'var(--text-secondary)',
                        border: `1px solid ${isEco ? 'var(--status-success-border)' : 'var(--border-color)'}`,
                        cursor: 'pointer',
                        fontSize: '11px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontWeight: 600,
                      }}
                    >
                      <Leaf size={12} />
                      <span>Éco</span>
                    </button>

                    <button
                      onClick={() => toggleAppareil(appareil.machine_id, appareil.nom, appareil.status)}
                      title={isActive ? 'Mettre hors ligne' : 'Activer'}
                      disabled={loadingMachineId === appareil.machine_id}
                      style={{
                        padding: '6px 10px',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: isActive ? 'var(--bg-card)' : 'var(--status-alert-bg)',
                        color: isActive ? 'var(--status-success)' : 'var(--status-alert)',
                        border: `1px solid ${isActive ? 'var(--border-color)' : 'var(--status-alert-border)'}`,
                        cursor: 'pointer',
                        fontSize: '11px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontWeight: 600,
                      }}
                    >
                      <Power size={12} />
                    </button>
                  </div>
                </div>
              );
            })}

            {machines.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px', padding: '24px' }}>
                Aucune machine enregistrée.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* =====================================================================
          HIÉRARCHIE 3 : PRÉDICTIONS IA & MODULES SPÉCIALISÉS (OCR / Multimédia)
      ===================================================================== */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px' }}>
        {/* Module OCR Facture (Ménage & PME) */}
        <InvoiceUploadWidget />

        {/* Module Vision Média Multimodal (PME & Industrie) */}
        <MediaAnalyzerWidget
          machines={machines.map((m) => ({ id: m.machine_id, nom: m.nom, site_nom: m.site_nom }))}
        />
      </div>

      {/* Toast */}
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
