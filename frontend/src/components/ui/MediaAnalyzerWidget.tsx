'use client';

import React, { useState } from 'react';
import { Camera, AlertOctagon, CheckCircle2, Loader2, ArrowRight, Video, UploadCloud, X } from 'lucide-react';
import { API_URL } from '@/lib/api';
import { ProvenanceBadge } from './ProvenanceBadge';

interface MediaAnalyzerWidgetProps {
  machineId?: string;
  machines?: Array<{ id: string; nom: string; site_nom?: string }>;
  onAnalysisCompleted?: (result: any) => void;
  style?: React.CSSProperties;
}

/**
 * MediaAnalyzerWidget — Analyse multimodale IA par vision par ordinateur (Gemini).
 * Détection de dangers physiques (fumée, fuites, surchauffe) sur photos et vidéos de machines.
 */
export function MediaAnalyzerWidget({
  machineId: initialMachineId,
  machines = [],
  onAnalysisCompleted,
  style = {},
}: MediaAnalyzerWidgetProps) {
  const [selectedMachineId, setSelectedMachineId] = useState(initialMachineId || (machines[0]?.id || ''));
  const [mediaFile, setMediaFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setMediaFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAnalysisResult(null);
      setError(null);
    }
  };

  const runMediaAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mediaFile || !selectedMachineId) return;

    setAnalyzing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', mediaFile);

    try {
      const res = await fetch(`${API_URL}/api/machines/${selectedMachineId}/analyze-media`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setAnalysisResult(data);
      if (onAnalysisCompleted) onAnalysisCompleted(data);
    } catch (err: any) {
      console.error("Erreur d'analyse média :", err);
      setError(err.message || "Impossible de contacter l'API d'analyse visuelle.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div
      className="card-standard"
      style={{
        padding: '24px',
        backgroundColor: 'var(--bg-card)',
        ...style,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Camera size={20} color="var(--accent-cta)" />
          <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Vision IA & Détection Visuelle
          </h3>
        </div>
        <ProvenanceBadge type="synthetique" label="Inférence Vision" />
      </div>

      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '18px', lineHeight: 1.5 }}>
        Téléversez une photo ou vidéo de votre équipement pour détecter automatiquement les anomalies physiques visibles (fumée, fuite, surchauffe ou amorçage).
      </p>

      {!analysisResult && (
        <form onSubmit={runMediaAnalysis}>
          {machines.length > 0 && !initialMachineId && (
            <div style={{ marginBottom: '14px' }}>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Équipement cible
              </label>
              <select
                value={selectedMachineId}
                onChange={(e) => setSelectedMachineId(e.target.value)}
                className="input-standard"
                required
              >
                <option value="">-- Sélectionner une machine --</option>
                {machines.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.nom} {m.site_nom ? `(${m.site_nom})` : ''}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div
            style={{
              border: '2px dashed var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '20px',
              textAlign: 'center',
              backgroundColor: 'var(--bg-surface)',
              cursor: 'pointer',
              marginBottom: '14px',
            }}
            onClick={() => document.getElementById('media-upload-input')?.click()}
          >
            <input
              id="media-upload-input"
              type="file"
              accept="image/*,video/*"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />

            <UploadCloud size={32} color="var(--accent-cta)" style={{ margin: '0 auto 8px auto' }} />

            {mediaFile ? (
              <div>
                <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>
                  {mediaFile.name}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {(mediaFile.size / (1024 * 1024)).toFixed(2)} Mo • Format prêt pour inspection IA
                </div>
              </div>
            ) : (
              <div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Sélectionnez une photo ou vidéo de l'équipement
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  PNG, JPG, MP4, WebM (Caméra mobile ou capteur optique)
                </div>
              </div>
            )}
          </div>

          {previewUrl && (
            <div style={{ marginBottom: '14px', borderRadius: 'var(--radius-sm)', overflow: 'hidden', maxHeight: '160px', display: 'flex', justifyContent: 'center', backgroundColor: '#000' }}>
              {mediaFile?.type.startsWith('image/') ? (
                <img src={previewUrl} alt="Aperçu" style={{ maxHeight: '160px', objectFit: 'contain' }} />
              ) : (
                <video src={previewUrl} controls style={{ maxHeight: '160px' }} />
              )}
            </div>
          )}

          {error && (
            <div style={{ padding: '10px 14px', backgroundColor: 'var(--status-alert-bg)', color: 'var(--status-alert)', borderRadius: 'var(--radius-sm)', fontSize: '12px', marginBottom: '12px' }}>
              {error}
            </div>
          )}

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              type="submit"
              disabled={!mediaFile || !selectedMachineId || analyzing}
              className="btn-cta"
              style={{ flex: 1 }}
            >
              {analyzing ? (
                <>
                  <Loader2 size={16} className="spin-slow" />
                  <span>Analyse multimodale en cours...</span>
                </>
              ) : (
                <>
                  <span>Lancer l'Inspection Visuelle</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
            {mediaFile && (
              <button
                type="button"
                onClick={() => { setMediaFile(null); setPreviewUrl(null); }}
                className="btn-outline"
                style={{ width: 'auto' }}
              >
                Effacer
              </button>
            )}
          </div>
        </form>
      )}

      {/* Résultat d'analyse */}
      {analysisResult && (
        <div className="animate-fade-in">
          <div
            style={{
              padding: '16px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: analysisResult.status === 'ALERTE' ? 'var(--status-alert-bg)' : 'var(--status-success-bg)',
              border: `1px solid ${analysisResult.status === 'ALERTE' ? 'var(--status-alert-border)' : 'var(--status-success-border)'}`,
              marginBottom: '14px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              {analysisResult.status === 'ALERTE' ? (
                <AlertOctagon size={20} color="var(--status-alert)" />
              ) : (
                <CheckCircle2 size={20} color="var(--status-success)" />
              )}
              <span
                style={{
                  fontSize: '13px',
                  fontWeight: 800,
                  color: analysisResult.status === 'ALERTE' ? 'var(--status-alert)' : 'var(--status-success)',
                  textTransform: 'uppercase',
                }}
              >
                {analysisResult.status === 'ALERTE' ? 'Danger / Incident Détecté' : 'Équipement Conforme & Sûr'}
              </span>
            </div>

            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
              {analysisResult.message}
            </div>

            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              <strong>Rapport IA :</strong> {analysisResult.description}
            </div>
          </div>

          <button
            onClick={() => { setAnalysisResult(null); setMediaFile(null); setPreviewUrl(null); }}
            className="btn-outline"
            style={{ width: '100%' }}
          >
            Analyser un autre média
          </button>
        </div>
      )}
    </div>
  );
}
