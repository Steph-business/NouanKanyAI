'use client';

import React, { useEffect, useState } from 'react';
import {
  Plug,
  Plus,
  Power,
  Leaf,
  Activity,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  Search,
  Filter,
  CheckCircle2,
  AlertOctagon,
  Sliders,
  Camera,
} from 'lucide-react';
import { API_URL } from '@/lib/api';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';
import { MediaAnalyzerWidget } from '@/components/ui/MediaAnalyzerWidget';
import { Toast, ToastMessage } from '@/components/ui/Toast';

export default function AppareilsPage() {
  const [machines, setMachines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [loadingActionId, setLoadingActionId] = useState<string | null>(null);

  // Simulation modal
  const [simulatingMachine, setSimulatingMachine] = useState<any | null>(null);
  const [simTemp, setSimTemp] = useState<number>(30);
  const [simPower, setSimPower] = useState<number>(50);
  const [simVibration, setSimVibration] = useState<number>(2.0);
  const [simPressure, setSimPressure] = useState<number>(1.2);

  // Toast
  const [toast, setToast] = useState<ToastMessage | null>(null);

  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    setToast({ id: Date.now().toString(), message, type });
  };

  const fetchMachines = async () => {
    try {
      const res = await fetch(`${API_URL}/api/machines`);
      const data = await res.json();
      setMachines(data);
    } catch (err) {
      console.error("Erreur chargement machines :", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMachines();
    const interval = setInterval(fetchMachines, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleToggle = async (machine_id: string, nom: string, current_status: string) => {
    setLoadingActionId(machine_id);
    try {
      await fetch(`${API_URL}/api/machines/${machine_id}/toggle`, { method: 'POST' });
      await fetchMachines();
      const isOff = ['actif', 'eco'].includes(current_status);
      showToast(isOff ? `${nom} mis hors tension.` : `${nom} remis sous tension.`, 'success');
    } catch (err) {
      showToast("Erreur lors de la commutation.", 'error');
    } finally {
      setLoadingActionId(null);
    }
  };

  const handleEco = async (machine_id: string, nom: string) => {
    setLoadingActionId(machine_id);
    try {
      await fetch(`${API_URL}/api/machines/${machine_id}/eco`, { method: 'POST' });
      await fetchMachines();
      showToast(`Mode Éco appliqué à ${nom} (-35% de puissance).`, 'success');
    } catch (err) {
      showToast("Erreur mode éco.", 'error');
    } finally {
      setLoadingActionId(null);
    }
  };

  const handleRunSimulation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!simulatingMachine) return;

    try {
      const res = await fetch(`${API_URL}/api/machines/${simulatingMachine.machine_id}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          temperature_c: Number(simTemp),
          power_kw: Number(simPower),
          vibration_hz: Number(simVibration),
          pressure_bar: Number(simPressure),
        }),
      });
      const data = await res.json();
      await fetchMachines();
      setSimulatingMachine(null);
      showToast(`Simulation injectée sur ${simulatingMachine.nom}. Détection d'anomalie mise à jour.`, 'info');
    } catch (err) {
      showToast("Erreur lors de l'injection des capteurs.", 'error');
    }
  };

  const filteredMachines = machines.filter((m) => {
    const matchesQuery = m.nom.toLowerCase().includes(searchQuery.toLowerCase()) || m.machine_id.toLowerCase().includes(searchQuery.toLowerCase());
    if (statusFilter === 'all') return matchesQuery;
    return matchesQuery && m.status === statusFilter;
  });

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cta)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Inventaire & Télégestion
            </span>
            <ProvenanceBadge type="mesure" label="Contrôle Direct" />
          </div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
            Gestion des Équipements
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
            Supervisez la consommation unitaire, enclenchez le mode éco ou simulez des scénarios de surcharge.
          </p>
        </div>
      </div>

      {/* Barre de filtres et recherche */}
      <div
        className="card-standard"
        style={{
          padding: '16px 20px',
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          backgroundColor: 'var(--bg-card)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, minWidth: '240px' }}>
          <Search size={16} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Rechercher une machine par nom ou identifiant..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-standard"
            style={{ minHeight: '36px', border: 'none', background: 'transparent' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>Statut :</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-standard"
            style={{ minHeight: '36px', padding: '4px 10px', fontSize: '12px', width: 'auto' }}
          >
            <option value="all">Tous les états ({machines.length})</option>
            <option value="actif">En service (Actif)</option>
            <option value="eco">Mode Éco (-35%)</option>
            <option value="alerte">En Alerte</option>
            <option value="inactif">Hors tension</option>
          </select>
        </div>
      </div>

      {/* Grille des Équipements */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        {filteredMachines.map((machine) => {
          const isEco = machine.status === 'eco';
          const isActive = ['actif', 'eco'].includes(machine.status);
          const isAlert = machine.status === 'alerte';

          return (
            <div
              key={machine.machine_id}
              className="card-standard"
              style={{
                padding: '20px',
                borderColor: isAlert ? 'var(--status-alert-border)' : undefined,
                backgroundColor: isAlert ? 'var(--status-alert-bg)' : 'var(--bg-card)',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              {/* Header de la carte */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span
                      style={{
                        width: '9px',
                        height: '9px',
                        borderRadius: '50%',
                        backgroundColor: isAlert ? 'var(--status-alert)' : isEco ? 'var(--status-warning)' : isActive ? 'var(--status-success)' : 'var(--text-muted)',
                      }}
                    />
                    <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                      {machine.nom}
                    </h3>
                  </div>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'IBM Plex Mono, monospace' }}>
                    ID: {machine.machine_id} {machine.site_nom ? `• ${machine.site_nom}` : ''}
                  </span>
                </div>

                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 800,
                    padding: '2px 8px',
                    borderRadius: '12px',
                    backgroundColor: isAlert ? 'var(--status-alert)' : isEco ? 'var(--status-warning-bg)' : isActive ? 'var(--status-success-bg)' : 'var(--bg-surface)',
                    color: isAlert ? '#FFFFFF' : isEco ? 'var(--status-warning)' : isActive ? 'var(--status-success)' : 'var(--text-muted)',
                    textTransform: 'uppercase',
                  }}
                >
                  {machine.status}
                </span>
              </div>

              {/* Télémétrie de l'appareil */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '10px',
                  padding: '12px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-surface)',
                  marginBottom: '16px',
                }}
              >
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Puissance</div>
                  <div className="tabular-numbers" style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'IBM Plex Mono, monospace' }}>
                    {machine.power_kw} <span style={{ fontSize: '11px', fontWeight: 600 }}>kW</span>
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Température</div>
                  <div className="tabular-numbers" style={{ fontSize: '16px', fontWeight: 800, color: machine.temperature_c > 75 ? 'var(--status-alert)' : 'var(--text-primary)', fontFamily: 'IBM Plex Mono, monospace' }}>
                    {machine.temperature_c?.toFixed(1)} <span style={{ fontSize: '11px', fontWeight: 600 }}>°C</span>
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Vibrations</div>
                  <div className="tabular-numbers" style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-secondary)', fontFamily: 'IBM Plex Mono, monospace' }}>
                    {machine.vibration_hz ? `${machine.vibration_hz} Hz` : 'N/A'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Pression</div>
                  <div className="tabular-numbers" style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-secondary)', fontFamily: 'IBM Plex Mono, monospace' }}>
                    {machine.pressure_bar ? `${machine.pressure_bar} bar` : 'N/A'}
                  </div>
                </div>
              </div>

              {/* Boutons d'action */}
              <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
                <button
                  onClick={() => handleEco(machine.machine_id, machine.nom)}
                  disabled={loadingActionId === machine.machine_id}
                  className="btn-ghost"
                  style={{
                    flex: 1,
                    justifyContent: 'center',
                    border: '1px solid var(--border-color)',
                    backgroundColor: isEco ? 'var(--status-success-bg)' : 'var(--bg-surface)',
                    color: isEco ? 'var(--status-success)' : 'var(--text-secondary)',
                  }}
                >
                  <Leaf size={14} />
                  <span>Mode Éco</span>
                </button>

                <button
                  onClick={() => handleToggle(machine.machine_id, machine.nom, machine.status)}
                  disabled={loadingActionId === machine.machine_id}
                  className="btn-ghost"
                  style={{
                    padding: '8px 12px',
                    border: '1px solid var(--border-color)',
                    backgroundColor: isActive ? 'var(--bg-surface)' : 'var(--status-alert-bg)',
                    color: isActive ? 'var(--status-success)' : 'var(--status-alert)',
                  }}
                  title={isActive ? 'Éteindre' : 'Allumer'}
                >
                  <Power size={15} />
                </button>

                <button
                  onClick={() => {
                    setSimulatingMachine(machine);
                    setSimPower(machine.power_kw);
                    setSimTemp(machine.temperature_c || 30);
                    setSimVibration(machine.vibration_hz || 2.0);
                    setSimPressure(machine.pressure_bar || 1.2);
                  }}
                  className="btn-ghost"
                  style={{
                    padding: '8px 12px',
                    border: '1px solid var(--border-color)',
                    color: 'var(--accent-cta)',
                  }}
                  title="Simuler capteurs"
                >
                  <Sliders size={15} />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Module Vision Média Multimodal */}
      <MediaAnalyzerWidget
        machines={machines.map((m) => ({ id: m.machine_id, nom: m.nom, site_nom: m.site_nom }))}
      />

      {/* Simulation Modal */}
      {simulatingMachine && (
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
          onClick={() => setSimulatingMachine(null)}
        >
          <div
            className="card-standard"
            style={{
              width: '100%',
              maxWidth: '480px',
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
                  Simulateur de Capteurs : {simulatingMachine.nom}
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Injectez des variations de charge pour tester les alertes en direct.
                </p>
              </div>
              <ProvenanceBadge type="synthetique" label="Simulation" />
            </div>

            <form onSubmit={handleRunSimulation} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  Puissance appelée (kW)
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={simPower}
                  onChange={(e) => setSimPower(parseFloat(e.target.value) || 0)}
                  className="input-standard tabular-numbers"
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  Température moteur (°C)
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={simTemp}
                  onChange={(e) => setSimTemp(parseFloat(e.target.value) || 0)}
                  className="input-standard tabular-numbers"
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                    Vibrations (Hz)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={simVibration}
                    onChange={(e) => setSimVibration(parseFloat(e.target.value) || 0)}
                    className="input-standard tabular-numbers"
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                    Pression (bar)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={simPressure}
                    onChange={(e) => setSimPressure(parseFloat(e.target.value) || 0)}
                    className="input-standard tabular-numbers"
                  />
                </div>
              </div>

              {/* Scénarios d'émulation */}
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={() => { setSimPower(35); setSimTemp(28); setSimVibration(1.5); setSimPressure(1.0); }}
                  className="btn-ghost"
                  style={{ fontSize: '11px', padding: '3px 8px', border: '1px solid var(--border-color)' }}
                >
                  🟢 Nominal
                </button>
                <button
                  type="button"
                  onClick={() => { setSimPower(180); setSimTemp(89); setSimVibration(24); setSimPressure(3.5); }}
                  className="btn-ghost"
                  style={{ fontSize: '11px', padding: '3px 8px', border: '1px solid var(--status-alert-border)', color: 'var(--status-alert)' }}
                >
                  🔴 Surchauffe Critique
                </button>
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <button type="submit" className="btn-cta" style={{ flex: 1 }}>
                  Injecter la Télémétrie
                </button>
                <button type="button" onClick={() => setSimulatingMachine(null)} className="btn-outline">
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Toast */}
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
