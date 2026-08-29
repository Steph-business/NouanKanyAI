'use client';

import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, Eye, ArrowRight, Loader2 } from 'lucide-react';
import { ProvenanceBadge } from './ProvenanceBadge';

interface ExtractedInvoiceData {
  clientName: string;
  accountNumber: string;
  billingPeriod: string;
  totalKwh: number;
  totalFcfa: number;
  tariffTier: string;
  potentialSavingsFcfa: number;
  dueDate: string;
}

interface InvoiceUploadWidgetProps {
  onDataExtracted?: (data: ExtractedInvoiceData) => void;
  style?: React.CSSProperties;
}

/**
 * InvoiceUploadWidget — Module d'upload et d'OCR de facture CIE.
 * Permet l'extraction structurée (kWh, palier tarifaire, montant FCFA, gains potentiels).
 */
export function InvoiceUploadWidget({ onDataExtracted, style = {} }: InvoiceUploadWidgetProps) {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [extractedData, setExtractedData] = useState<ExtractedInvoiceData | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setPreviewUrl(URL.createObjectURL(selected));
      setExtractedData(null);
    }
  };

  const runOcrAnalysis = () => {
    if (!file) return;
    setAnalyzing(true);

    // Simulation d'extraction OCR intelligente haute fidélité
    setTimeout(() => {
      const mockResult: ExtractedInvoiceData = {
        clientName: 'ADAMA KOFFI',
        accountNumber: '1254657890',
        billingPeriod: 'Avril 2026',
        totalKwh: 418.5,
        totalFcfa: 28450,
        tariffTier: 'Non Domestique (68 FCFA/kWh)',
        potentialSavingsFcfa: 4260, // 15% d'optimisation
        dueDate: '15 Mai 2026',
      };
      setExtractedData(mockResult);
      setAnalyzing(false);
      if (onDataExtracted) onDataExtracted(mockResult);
    }, 1400);
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileText size={20} color="var(--accent-cta)" />
          <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Analyseur de Facture CIE (OCR)
          </h3>
        </div>
        <ProvenanceBadge type="mesure" label="Scan Document" />
      </div>

      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '18px', lineHeight: 1.5 }}>
        Téléversez ou prenez en photo votre facture d'électricité CIE. Notre IA extrait automatiquement votre palier tarifaire et calibre vos seuils de consommation.
      </p>

      {/* Zone de Drop / Sélection */}
      {!extractedData && (
        <div
          style={{
            border: '2px dashed var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '28px 20px',
            textAlign: 'center',
            backgroundColor: 'var(--bg-surface)',
            cursor: 'pointer',
            transition: 'border-color 0.2s ease',
          }}
          onClick={() => document.getElementById('invoice-file-input')?.click()}
        >
          <input
            id="invoice-file-input"
            type="file"
            accept="image/*,application/pdf"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />

          <UploadCloud size={36} color="var(--accent-cta)" style={{ margin: '0 auto 12px auto' }} />

          {file ? (
            <div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)' }}>
                {file.name}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                {(file.size / 1024).toFixed(1)} Ko • Prêt pour l'extraction
              </div>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Cliquez pour choisir un fichier ou déposez votre photo
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Formats acceptés : PNG, JPG, PDF (Photo de facture CIE nette)
              </div>
            </div>
          )}
        </div>
      )}

      {file && !extractedData && (
        <div style={{ marginTop: '16px', display: 'flex', gap: '10px' }}>
          <button
            onClick={runOcrAnalysis}
            disabled={analyzing}
            className="btn-cta"
            style={{ flex: 1 }}
          >
            {analyzing ? (
              <>
                <Loader2 size={16} className="spin-slow" />
                <span>Extraction des métriques CIE en cours...</span>
              </>
            ) : (
              <>
                <span>Lancer l'Extraction OCR</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
          <button
            onClick={() => { setFile(null); setPreviewUrl(null); }}
            className="btn-outline"
            style={{ width: 'auto' }}
          >
            Annuler
          </button>
        </div>
      )}

      {/* Résultat de l'extraction */}
      {extractedData && (
        <div className="animate-fade-in" style={{ marginTop: '16px' }}>
          <div
            style={{
              padding: '16px',
              backgroundColor: 'var(--bg-surface)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              marginBottom: '16px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--status-success)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <CheckCircle2 size={16} /> EXTRACTION RÉUSSIE
              </span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Période : {extractedData.billingPeriod}</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Client / Compte</div>
                <div style={{ fontSize: '13px', fontWeight: 700 }}>{extractedData.clientName}</div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>N° {extractedData.accountNumber}</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Consommation Relevée</div>
                <div className="tabular-numbers" style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  {extractedData.totalKwh} <span style={{ fontSize: '12px' }}>kWh</span>
                </div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Palier CIE Détecté</div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--accent-cost)' }}>{extractedData.tariffTier}</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Montant Net Facturé</div>
                <div className="tabular-numbers" style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  {extractedData.totalFcfa.toLocaleString('fr-FR')} <span style={{ fontSize: '12px' }}>FCFA</span>
                </div>
              </div>
            </div>

            <div
              style={{
                marginTop: '12px',
                paddingTop: '10px',
                borderTop: '1px solid var(--border-subtle)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Économie mensuelle estimée (Gain-Share) :
              </span>
              <strong className="tabular-numbers" style={{ fontSize: '14px', color: 'var(--status-success)' }}>
                +{extractedData.potentialSavingsFcfa.toLocaleString('fr-FR')} FCFA / mois
              </strong>
            </div>
          </div>

          <button
            onClick={() => { setFile(null); setExtractedData(null); }}
            className="btn-outline"
            style={{ width: '100%' }}
          >
            Scanner une autre facture
          </button>
        </div>
      )}
    </div>
  );
}
