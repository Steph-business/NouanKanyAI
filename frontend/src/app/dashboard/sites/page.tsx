'use client';

import React, { useState, useEffect } from 'react';
import { Factory, Plus, MapPin, Activity, Plug, ArrowRight, X } from 'lucide-react';
import { API_URL } from '@/lib/api';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';
import { Toast, ToastMessage } from '@/components/ui/Toast';

export default function SitesPage() {
  const [sites, setSites] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newSiteNom, setNewSiteNom] = useState('');
  const [newSiteVille, setNewSiteVille] = useState('Abidjan');
  const [newSiteType, setNewSiteType] = useState('Usine');

  // Toast
  const [toast, setToast] = useState<ToastMessage | null>(null);

  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    setToast({ id: Date.now().toString(), message, type });
  };

  const fetchSites = async () => {
    try {
      const res = await fetch(`${API_URL}/api/sites`);
      const data = await res.json();
      setSites(data);
    } catch (err) {
      console.error("Erreur chargement sites:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSites();
  }, []);

  const handleAddSite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSiteNom) return;

    try {
      await fetch(`${API_URL}/api/sites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nom: newSiteNom,
          ville: newSiteVille,
          type: newSiteType,
        }),
      });
      await fetchSites();
      setIsAddModalOpen(false);
      setNewSiteNom('');
      showToast(`Site "${newSiteNom}" ajouté avec succès.`, 'success');
    } catch (err) {
      showToast("Erreur lors de l'ajout du site.", 'error');
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cta)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Supervision Multi-Sites
            </span>
            <ProvenanceBadge type="mesure" label="Réseau Abidjan" />
          </div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
            Sites & Lieux d'Exploitation
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
            Consolidez la consommation énergétique de l'ensemble de vos filiales, usines et magasins.
          </p>
        </div>

        <button
          onClick={() => setIsAddModalOpen(true)}
          className="btn-cta"
          style={{ fontSize: '13px', padding: '10px 18px' }}
        >
          <Plus size={16} />
          <span>Ajouter un Site</span>
        </button>
      </div>

      {/* Grille des Sites */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        {sites.map((site) => (
          <div
            key={site.site_id || site.id}
            className="card-standard"
            style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Factory size={18} color="var(--accent-cta)" />
                  <h3 style={{ fontSize: '17px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                    {site.nom}
                  </h3>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  <MapPin size={12} color="var(--text-muted)" />
                  <span>{site.ville || 'Abidjan'} • {site.type || 'Industrie'}</span>
                </div>
              </div>

              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 800,
                  color: 'var(--status-success)',
                  backgroundColor: 'var(--status-success-bg)',
                  padding: '3px 8px',
                  borderRadius: '12px',
                }}
              >
                EN LIGNE
              </span>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '10px',
                padding: '14px',
                backgroundColor: 'var(--bg-surface)',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '16px',
              }}
            >
              <div>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Équipements</div>
                <div className="tabular-numbers" style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'IBM Plex Mono, monospace' }}>
                  {site.machines_count || 4}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Charge Moyenne</div>
                <div className="tabular-numbers" style={{ fontSize: '18px', fontWeight: 800, color: 'var(--accent-cost)', fontFamily: 'IBM Plex Mono, monospace' }}>
                  {site.total_kw || 48.5} <span style={{ fontSize: '12px' }}>kW</span>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Seuil max : <strong>120 kW</strong>
              </span>
              <ProvenanceBadge type="mesure" label="Réseau" />
            </div>
          </div>
        ))}

        {sites.length === 0 && !loading && (
          <div className="card-standard" style={{ padding: '36px', textAlign: 'center', gridColumn: '1 / -1' }}>
            <p style={{ color: 'var(--text-secondary)' }}>Aucun site configuré. Cliquez sur "Ajouter un Site" pour démarrer.</p>
          </div>
        )}
      </div>

      {/* Modal Ajout de Site */}
      {isAddModalOpen && (
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
          onClick={() => setIsAddModalOpen(false)}
        >
          <div
            className="card-standard"
            style={{
              width: '100%',
              maxWidth: '440px',
              backgroundColor: 'var(--bg-elevated)',
              boxShadow: 'var(--shadow-dropdown)',
              borderRadius: 'var(--radius-lg)',
              padding: '28px',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
                Nouveau Site d'Exploitation
              </h3>
              <button onClick={() => setIsAddModalOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleAddSite} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  Nom du site ou filiale
                </label>
                <input
                  type="text"
                  placeholder="Ex: Usine Yopougon Zone Industrielle"
                  value={newSiteNom}
                  onChange={(e) => setNewSiteNom(e.target.value)}
                  className="input-standard"
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  Ville / Commune
                </label>
                <input
                  type="text"
                  placeholder="Abidjan"
                  value={newSiteVille}
                  onChange={(e) => setNewSiteVille(e.target.value)}
                  className="input-standard"
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  Type d'installation
                </label>
                <select
                  value={newSiteType}
                  onChange={(e) => setNewSiteType(e.target.value)}
                  className="input-standard"
                >
                  <option value="Usine">Usine / Industrie Lourde</option>
                  <option value="Commerce">Commerce / Supermarché</option>
                  <option value="Bureaux">Bâtiment Tertiaire & Bureaux</option>
                  <option value="Atelier">Atelier / Entrepôt Frigorifique</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
                <button type="submit" className="btn-cta" style={{ flex: 1 }}>
                  Enregistrer le Site
                </button>
                <button type="button" onClick={() => setIsAddModalOpen(false)} className="btn-outline">
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
