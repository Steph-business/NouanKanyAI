'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import {
  Zap,
  ArrowRight,
  ShieldCheck,
  Cpu,
  FileText,
  TrendingUp,
  Activity,
  Layers,
  Building2,
  Home as HomeIcon,
  Factory,
  Lock,
  Mail,
  CheckCircle2,
  Sparkles,
  HelpCircle,
  X,
  ChevronRight,
} from 'lucide-react';
import { supabase } from '@/lib/supabase';
import { CieTariffBar } from '@/components/ui/CieTariffBar';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';
import { LevelSelector, UserLevel } from '@/components/ui/LevelSelector';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { Toast, ToastMessage } from '@/components/ui/Toast';

export default function LandingPage() {
  const router = useRouter();

  // Auth modal states
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [nom, setNom] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [typeCompte, setTypeCompte] = useState('Industriel');
  const [loading, setLoading] = useState(false);

  // Newsletter state
  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [newsletterSent, setNewsletterSent] = useState(false);

  // Interactive Level Selector on Segment Cards
  const [householdLevel, setHouseholdLevel] = useState<UserLevel>('debutant');
  const [smeLevel, setSmeLevel] = useState<UserLevel>('amateur');
  const [industryLevel, setIndustryLevel] = useState<UserLevel>('technique');

  // Toast
  const [toast, setToast] = useState<ToastMessage | null>(null);

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ id: Date.now().toString(), message, type });
  };

  useEffect(() => {
    const checkSession = async () => {
      if (!supabase) {
        return;
      }
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        // user already logged in
      }
    };
    checkSession();
  }, [router]);

  const handleQuickDemoLogin = (profile: 'Ménage' | 'PME' | 'Industriel' | 'Admin') => {
    const mockUsers = {
      Ménage: { nom: 'Koffi Adama', email: 'koffi.adama@nouankanyai.ci', type_compte: 'Ménage', level: 'debutant' },
      PME: { nom: 'Épicerie Fine Adjamé', email: 'contact@epicerie-adjame.ci', type_compte: 'PME', level: 'amateur' },
      Industriel: { nom: 'Stephy Koutouan', email: 'stephykoutouandah@gmail.com', type_compte: 'Industriel', level: 'technique' },
      Admin: { nom: 'John Oba', email: 'john.oba@nouankanyai.ci', type_compte: 'Admin', level: 'technique' },
    };

    const selected = mockUsers[profile];
    localStorage.setItem('mockUser', JSON.stringify(selected));
    localStorage.setItem('nouankanyai_profile', profile);
    localStorage.setItem('nouankanyai_level', selected.level);

    showToast(`Connexion à l'espace ${profile} en cours...`, 'success');
    setTimeout(() => {
      if (profile === 'Admin') {
        router.push('/dashboard/admin');
      } else {
        router.push('/dashboard');
      }
    }, 600);
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const mockUser = {
      nom: nom || email.split('@')[0],
      email: email,
      type_compte: typeCompte,
      level: typeCompte === 'Particulier' ? 'debutant' : typeCompte === 'Entreprise' ? 'amateur' : 'technique',
    };
    localStorage.setItem('mockUser', JSON.stringify(mockUser));
    localStorage.setItem('nouankanyai_profile', typeCompte);
    localStorage.setItem('nouankanyai_level', mockUser.level);

    showToast("Connexion validée. Redirection vers votre tableau de bord...", 'success');
    setTimeout(() => {
      router.push('/dashboard');
    }, 800);
  };

  const handleNewsletterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newsletterEmail) return;
    setNewsletterSent(true);
    showToast("Merci pour votre inscription à la liste d'accès anticipé.", 'success');
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      {/* 1. STICKY NAV */}
      <header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 1000,
          backgroundColor: 'var(--bg-card)',
          borderBottom: '1px solid var(--border-color)',
          backdropFilter: 'blur(8px)',
        }}
      >
        <div
          style={{
            maxWidth: '1240px',
            margin: '0 auto',
            padding: '0 24px',
            height: '68px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          {/* Logo */}
          <div
            onClick={() => router.push('/')}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
          >
            <Image
              src="/NouankanyAI.png"
              alt="NouanKanyAI Logo"
              width={38}
              height={38}
              style={{ objectFit: 'contain' }}
              priority
            />
            <div>
              <span style={{ fontSize: '19px', fontWeight: 800, fontFamily: 'Space Grotesk, sans-serif', letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
                NouanKanyAI
              </span>
              <div style={{ fontSize: '9px', fontWeight: 700, color: 'var(--text-secondary)', letterSpacing: '0.08em' }}>
                MAÎTRISE ÉNERGÉTIQUE CIE
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav style={{ display: 'flex', alignItems: 'center', gap: '28px' }} className="desktop-nav">
            <a href="#constat" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', transition: 'color 0.15s' }}>
              Le Constat
            </a>
            <a href="#pour-qui" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', transition: 'color 0.15s' }}>
              Pour Qui
            </a>
            <a href="#notre-engagement" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', transition: 'color 0.15s' }}>
              Transparence
            </a>
            <a href="#formules" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', transition: 'color 0.15s' }}>
              Formules
            </a>
            <a href="#qui-sommes-nous" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', transition: 'color 0.15s' }}>
              À Propos
            </a>
          </nav>

          {/* Right Action buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <ThemeToggle />
            <button
              onClick={() => {
                setAuthMode('login');
                setIsAuthModalOpen(true);
              }}
              className="btn-outline"
              style={{ minHeight: '38px', padding: '8px 16px', fontSize: '13px' }}
            >
              Connexion
            </button>
            <button
              onClick={() => handleQuickDemoLogin('Industriel')}
              className="btn-cta"
              style={{ minHeight: '38px', padding: '8px 18px', fontSize: '13px' }}
            >
              <span>Accès Démo 1-Clic</span>
              <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </header>

      {/* 2. HERO SECTION */}
      <section
        style={{
          maxWidth: '1240px',
          margin: '0 auto',
          padding: '64px 24px 48px 24px',
        }}
      >
        <div style={{ maxWidth: '840px', marginBottom: '36px' }}>
          {/* Action Workflow Pipeline */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-full)',
              marginBottom: '20px',
              fontSize: '12px',
              color: 'var(--text-secondary)',
              fontWeight: 600,
              flexWrap: 'wrap',
            }}
          >
            <span>Upload Facture</span>
            <ChevronRight size={12} color="var(--text-muted)" />
            <span>OCR Automatique</span>
            <ChevronRight size={12} color="var(--text-muted)" />
            <span>Prédiction XGBoost</span>
            <ChevronRight size={12} color="var(--text-muted)" />
            <span style={{ color: 'var(--status-success)', fontWeight: 700 }}>Économies en FCFA</span>
          </div>

          <h1
            style={{
              fontSize: '44px',
              fontWeight: 800,
              color: 'var(--text-primary)',
              lineHeight: 1.15,
              letterSpacing: '-0.03em',
              marginBottom: '20px',
            }}
          >
            Maîtrisez votre consommation d'électricité avant la facturation CIE.
          </h1>

          <p
            style={{
              fontSize: '18px',
              color: 'var(--text-secondary)',
              lineHeight: 1.6,
              marginBottom: '32px',
              maxWidth: '720px',
            }}
          >
            Conçue pour les ménages, commerces, PME et industries en Côte d'Ivoire. Analysez vos index, anticipez les dépassements de puissance et appliquez des actions d'optimisation vérifiées.
          </p>

          <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center' }}>
            <button
              onClick={() => handleQuickDemoLogin('PME')}
              className="btn-cta"
              style={{ fontSize: '15px', padding: '14px 28px' }}
            >
              <span>Explorer la Plateforme (Démo)</span>
              <ArrowRight size={16} />
            </button>
            <button
              onClick={() => {
                setAuthMode('register');
                setIsAuthModalOpen(true);
              }}
              className="btn-outline"
              style={{ fontSize: '15px', padding: '14px 24px' }}
            >
              Créer un Compte
            </button>
          </div>
        </div>

        {/* Barre de Paliers Tarifaires CIE Interactive */}
        <CieTariffBar currentKwh={240} showDetails={true} interactive={true} />
      </section>

      {/* 3. PREUVES VISUELLES DE TERRAIN (Galerie photos authentiques) */}
      <section
        style={{
          backgroundColor: 'var(--bg-surface)',
          borderTop: '1px solid var(--border-color)',
          borderBottom: '1px solid var(--border-color)',
          padding: '56px 24px',
        }}
      >
        <div style={{ maxWidth: '1240px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '28px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-secondary)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '4px' }}>
                RÉALITÉ DU TERRAIN IVOIRIEN
              </div>
              <h2 style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-primary)' }}>
                Une solution ancrée dans le quotidien local
              </h2>
            </div>
            <ProvenanceBadge type="mesure" label="Photographies Terrain" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
            {/* Photo 1: Facture */}
            <div className="card-standard" style={{ padding: '0', overflow: 'hidden' }}>
              <div style={{ position: 'relative', height: '220px', width: '100%' }}>
                <Image
                  src="/photos/facture_cie_smartphone.jpg"
                  alt="Numérisation facture CIE smartphone"
                  fill
                  style={{ objectFit: 'cover' }}
                />
              </div>
              <div style={{ padding: '18px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 700 }}>Extraction Numérique OCR</span>
                  <ProvenanceBadge type="mesure" label="Papier CIE" />
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
                  Numérisation instantanée des index et tranches tarifaires depuis votre smartphone.
                </p>
              </div>
            </div>

            {/* Photo 2: Compteur */}
            <div className="card-standard" style={{ padding: '0', overflow: 'hidden' }}>
              <div style={{ position: 'relative', height: '220px', width: '100%' }}>
                <Image
                  src="/photos/compteur_electrique_cie.jpg"
                  alt="Compteur électrique CIE Abidjan"
                  fill
                  style={{ objectFit: 'cover' }}
                />
              </div>
              <div style={{ padding: '18px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 700 }}>Suivi des Compteurs</span>
                  <ProvenanceBadge type="mesure" label="Réseau Abidjan" />
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
                  Compatibilité avec les compteurs électromécaniques et électroniques installés en Côte d'Ivoire.
                </p>
              </div>
            </div>

            {/* Photo 3: Industrie */}
            <div className="card-standard" style={{ padding: '0', overflow: 'hidden' }}>
              <div style={{ position: 'relative', height: '220px', width: '100%' }}>
                <Image
                  src="/photos/technicien_tableau_industriel.jpg"
                  alt="Technicien tableau électrique industriel"
                  fill
                  style={{ objectFit: 'cover' }}
                />
              </div>
              <div style={{ padding: '18px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 700 }}>Supervision Industrielle</span>
                  <ProvenanceBadge type="synthetique" label="Modélisation ML" />
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
                  Diagnostic multi-paramétrique (puissance, échauffement, vibrations) pour machines lourdes.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. LE CONSTAT (3 Stats chiffrées) */}
      <section id="constat" style={{ maxWidth: '1240px', margin: '0 auto', padding: '64px 24px' }}>
        <div style={{ textAlign: 'center', maxWidth: '640px', margin: '0 auto 48px auto' }}>
          <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cost)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '6px' }}>
            ENJEUX ÉNERGÉTIQUES
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Le coût de l'électricité ne doit plus être une fatalité.
          </h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
          <div className="card-standard" style={{ padding: '28px' }}>
            <div className="tabular-numbers" style={{ fontSize: '38px', fontWeight: 800, color: 'var(--accent-cost)', fontFamily: 'IBM Plex Mono, monospace', marginBottom: '10px' }}>
              30% à 45%
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '8px' }}>Poids sur les charges d'exploitation</h3>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              La facture électrique représente le deuxième poste de dépense récurrent des PME et commerces équipés de froid à Abidjan.
            </p>
          </div>

          <div className="card-standard" style={{ padding: '28px' }}>
            <div className="tabular-numbers" style={{ fontSize: '38px', fontWeight: 800, color: 'var(--status-alert)', fontFamily: 'IBM Plex Mono, monospace', marginBottom: '10px' }}>
              x 2.66
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '8px' }}>Écart entre tranches tarifaires CIE</h3>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Le tarif passe de 36 FCFA à 96 FCFA/kWh lors du franchissement des paliers de puissance, entraînant des surcoûts brutaux.
            </p>
          </div>

          <div className="card-standard" style={{ padding: '28px' }}>
            <div className="tabular-numbers" style={{ fontSize: '38px', fontWeight: 800, color: 'var(--status-success)', fontFamily: 'IBM Plex Mono, monospace', marginBottom: '10px' }}>
              15% à 25%
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '8px' }}>Économies réalisables sans coupure</h3>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Un ajustement préventif des plages horaires et des modes d'alimentation permet de réduire la facture sans compromettre l'activité.
            </p>
          </div>
        </div>
      </section>

      {/* 5. POUR QUI (3 Cartes Segment avec Sélecteur de Niveau) */}
      <section id="pour-qui" style={{ backgroundColor: 'var(--bg-surface)', padding: '64px 24px', borderTop: '1px solid var(--border-color)', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ maxWidth: '1240px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', maxWidth: '640px', margin: '0 auto 48px auto' }}>
            <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cta)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '6px' }}>
              PRODUIT ADAPTÉ
            </div>
            <h2 style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)' }}>
              Une plateforme unique, trois profils d'usage
            </h2>
            <p style={{ fontSize: '15px', color: 'var(--text-secondary)', marginTop: '8px' }}>
              Le design system reste unifié. La granularité des données et le niveau de technicité s'adaptent à vos besoins.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '28px' }}>
            {/* Segment 1 : Ménages */}
            <div className="card-segment" style={{ padding: 0, display: 'flex', flexDirection: 'column' }}>
              <div style={{ position: 'relative', height: '180px', width: '100%' }}>
                <Image
                  src="/photos/foyer_ivoirien_quotidien.jpg"
                  alt="Ménage ivoirien"
                  fill
                  style={{ objectFit: 'cover' }}
                />
              </div>
              <div style={{ padding: '24px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <HomeIcon size={18} color="var(--accent-cta)" />
                    <h3 style={{ fontSize: '18px', fontWeight: 800 }}>Ménages</h3>
                  </div>
                  <LevelSelector currentLevel={householdLevel} onSelectLevel={setHouseholdLevel} size="sm" />
                </div>

                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '16px' }}>
                  Contrôlez votre budget familial avec un seuil global d'alerte, l'OCR de facture et des conseils simples par appareil.
                </p>

                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 20px 0', fontSize: '13px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={14} color="var(--status-success)" />
                    <span>Upload facture CIE par photo</span>
                  </li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={14} color="var(--status-success)" />
                    <span>Alerte dépassement de tranche sociale/domestique</span>
                  </li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={14} color="var(--status-success)" />
                    <span>Assistant conversationnel sur smartphone</span>
                  </li>
                </ul>

                <button
                  onClick={() => handleQuickDemoLogin('Ménage')}
                  className="btn-outline"
                  style={{ marginTop: 'auto', width: '100%', justifyContent: 'center' }}
                >
                  Voir la vue Ménage
                </button>
              </div>
            </div>

            {/* Segment 2 : PME */}
            <div className="card-segment" style={{ padding: 0, display: 'flex', flexDirection: 'column' }}>
              <div style={{ position: 'relative', height: '180px', width: '100%' }}>
                <Image
                  src="/photos/commerce_pme_abidjan.jpg"
                  alt="Commerce PME Abidjan"
                  fill
                  style={{ objectFit: 'cover' }}
                />
              </div>
              <div style={{ padding: '24px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Building2 size={18} color="var(--accent-cta)" />
                    <h3 style={{ fontSize: '18px', fontWeight: 800 }}>PME & Commerces</h3>
                  </div>
                  <LevelSelector currentLevel={smeLevel} onSelectLevel={setSmeLevel} size="sm" />
                </div>

                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '16px' }}>
                  Protégez votre marge commerciale : suivi par machine (chambre froide, fours), alertes de surcharge et rapports hebdomadaires.
                </p>

                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 20px 0', fontSize: '13px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={14} color="var(--status-success)" />
                    <span>Inventaire machines & puissance nominale</span>
                  </li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={14} color="var(--status-success)" />
                    <span>Analyse photo/vidéo des équipements</span>
                  </li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={14} color="var(--status-success)" />
                    <span>Rapports de marge sans jargon technique</span>
                  </li>
                </ul>

                <button
                  onClick={() => handleQuickDemoLogin('PME')}
                  className="btn-outline"
                  style={{ marginTop: 'auto', width: '100%', justifyContent: 'center' }}
                >
                  Voir la vue PME
                </button>
              </div>
            </div>

            {/* Segment 3 : Industrie */}
            <div className="card-segment" style={{ padding: 0, display: 'flex', flexDirection: 'column' }}>
              <div style={{ position: 'relative', height: '180px', width: '100%' }}>
                <Image
                  src="/photos/technicien_tableau_industriel.jpg"
                  alt="Industrie électrique"
                  fill
                  style={{ objectFit: 'cover' }}
                />
              </div>
              <div style={{ padding: '24px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Factory size={18} color="var(--accent-cta)" />
                    <h3 style={{ fontSize: '18px', fontWeight: 800 }}>Industrie</h3>
                  </div>
                  <LevelSelector currentLevel={industryLevel} onSelectLevel={setIndustryLevel} size="sm" />
                </div>

                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '16px' }}>
                  Haute précision opérationnelle : XGBoost t+1h, Isolation Forest (anomalies thermiques et vibratoires), audit et plan d'action chiffré.
                </p>

                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 20px 0', fontSize: '13px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={14} color="var(--status-success)" />
                    <span>Télémétrie complète (kW, °C, Hz, bar)</span>
                  </li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={14} color="var(--status-success)" />
                    <span>Détection d'anomalie Isolation Forest</span>
                  </li>
                  <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={14} color="var(--status-success)" />
                    <span>Rapports automatisés PDF, DOCX, XLSX</span>
                  </li>
                </ul>

                <button
                  onClick={() => handleQuickDemoLogin('Industriel')}
                  className="btn-cta"
                  style={{ marginTop: 'auto', width: '100%', justifyContent: 'center' }}
                >
                  Voir la vue Industrie
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. QUI SOMMES-NOUS */}
      <section id="qui-sommes-nous" style={{ maxWidth: '1240px', margin: '0 auto', padding: '64px 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '40px', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cta)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '6px' }}>
              ORIGINE DU PROJET
            </div>
            <h2 style={{ fontSize: '30px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '16px' }}>
              Née du Global AI Hackathon 2026
            </h2>
            <p style={{ fontSize: '15px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '16px' }}>
              NouanKanyAI est issue du programme d'accélération <strong>FORPRODE IA (Tech Talent Accelerator, soutenu par la GIZ)</strong> en Côte d'Ivoire.
            </p>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '24px' }}>
              Notre équipe d'ingénieurs en intelligence artificielle et spécialistes de l'énergie conçoit des outils logiciels robustes pour transformer la gestion énergétique en avantage concurrentiel en Afrique subsaharienne.
            </p>
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              <div style={{ padding: '12px 18px', backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Programme</div>
                <div style={{ fontSize: '14px', fontWeight: 700 }}>FORPRODE IA / GIZ</div>
              </div>
              <div style={{ padding: '12px 18px', backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Moteurs ML</div>
                <div style={{ fontSize: '14px', fontWeight: 700 }}>XGBoost & Isolation Forest</div>
              </div>
            </div>
          </div>

          <div className="card-standard" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ position: 'relative', height: '320px', width: '100%' }}>
              <Image
                src="/photos/equipe_forprode_hackathon.jpg"
                alt="Équipe NouanKanyAI Hackathon FORPRODE"
                fill
                style={{ objectFit: 'cover' }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* 7. NOTRE ENGAGEMENT DE TRANSPARENCE */}
      <section id="notre-engagement" style={{ backgroundColor: 'var(--bg-surface)', padding: '56px 24px', borderTop: '1px solid var(--border-color)', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ maxWidth: '840px', margin: '0 auto', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--status-success)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '6px' }}>
            HONNÊTETÉ PRODUIT
          </div>
          <h2 style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '16px' }}>
            Une donnée est mesurée, estimée ou synthétique. Jamais inventée.
          </h2>
          <p style={{ fontSize: '15px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '28px' }}>
            NouanKanyAI est en phase de déploiement logiciel actif. Aucun capteur physique IoT n'étant encore commercialisé sur site, nous identifions systématiquement la nature de chaque donnée affichée.
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
            <div style={{ padding: '16px 20px', backgroundColor: 'var(--bg-card)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', textAlign: 'left', minWidth: '220px' }}>
              <div style={{ marginBottom: '6px' }}>
                <ProvenanceBadge type="mesure" />
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Données réelles issues de documents officiels CIE ou relevés manuels.
              </div>
            </div>

            <div style={{ padding: '16px 20px', backgroundColor: 'var(--bg-card)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', textAlign: 'left', minWidth: '220px' }}>
              <div style={{ marginBottom: '6px' }}>
                <ProvenanceBadge type="estime" />
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Extrapolations basées sur la grille tarifaire officielle CIE.
              </div>
            </div>

            <div style={{ padding: '16px 20px', backgroundColor: 'var(--bg-card)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', textAlign: 'left', minWidth: '220px' }}>
              <div style={{ marginBottom: '6px' }}>
                <ProvenanceBadge type="synthetique" />
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Données calibrées par simulation pour l'entraînement des modèles ML.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 8. FORMULES & PRICING (Gain-Share 10%) */}
      <section id="formules" style={{ maxWidth: '1240px', margin: '0 auto', padding: '64px 24px' }}>
        <div style={{ textAlign: 'center', maxWidth: '640px', margin: '0 auto 48px auto' }}>
          <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-cta)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '6px' }}>
            MODÈLE ÉCONOMIQUE
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Partage de valeur : 10% sur les économies réelles
          </h2>
          <p style={{ fontSize: '15px', color: 'var(--text-secondary)', marginTop: '8px' }}>
            Nous ne gagnons que si vous réduisez votre facture. Aucun frais caché.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px', alignItems: 'stretch' }}>
          {/* Formule 1 */}
          <div className="card-standard" style={{ padding: '32px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
              Essentiel
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '8px' }}>Ménages</h3>
            <div className="tabular-numbers" style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'IBM Plex Mono, monospace', marginBottom: '16px' }}>
              Gratuit <span style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-muted)' }}>/ mois</span>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: 1.5 }}>
              Idéal pour suivre sa facture CIE mensuelle et détecter les dépassements de palier.
            </p>

            <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 28px 0', fontSize: '13px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={15} color="var(--status-success)" />
                <span>Upload facture OCR illimité</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={15} color="var(--status-success)" />
                <span>Historique 30 jours</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={15} color="var(--status-success)" />
                <span>Conseils de réduction de charge</span>
              </li>
            </ul>

            <button
              onClick={() => handleQuickDemoLogin('Ménage')}
              className="btn-outline"
              style={{ marginTop: 'auto', width: '100%' }}
            >
              Démarrer Gratuitement
            </button>
          </div>

          {/* Formule 2 : Recommandée / Ruban */}
          <div
            className="card-segment"
            style={{
              padding: '32px',
              display: 'flex',
              flexDirection: 'column',
              borderColor: 'var(--accent-cta)',
              borderWidth: '2px',
            }}
          >
            {/* Ruban */}
            <div
              style={{
                position: 'absolute',
                top: '0',
                right: '28px',
                backgroundColor: 'var(--accent-cta)',
                color: '#FFFFFF',
                fontSize: '11px',
                fontWeight: 800,
                padding: '4px 12px',
                borderRadius: '0 0 6px 6px',
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
              }}
            >
              Formule Recommandée
            </div>

            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--accent-cta)', textTransform: 'uppercase', marginBottom: '6px' }}>
              Gain-Share
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '8px' }}>PME & Commerces</h3>
            <div className="tabular-numbers" style={{ fontSize: '32px', fontWeight: 800, color: 'var(--accent-cta)', fontFamily: 'IBM Plex Mono, monospace', marginBottom: '16px' }}>
              10% <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-secondary)' }}>des économies réelles</span>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: 1.5 }}>
              Vous conservez 90% des économies financières générées sur votre facture.
            </p>

            <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 28px 0', fontSize: '13px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={15} color="var(--status-success)" />
                <span>Supervision jusqu'à 20 équipements</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={15} color="var(--status-success)" />
                <span>Rapports d'impact hebdomadaires</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={15} color="var(--status-success)" />
                <span>Règlement Mobile Money (Wave, Orange, MTN, Moov)</span>
              </li>
            </ul>

            <button
              onClick={() => handleQuickDemoLogin('PME')}
              className="btn-cta"
              style={{ marginTop: 'auto', width: '100%' }}
            >
              Activer l'Optimisation PME
            </button>
          </div>

          {/* Formule 3 : Entreprise */}
          <div className="card-standard" style={{ padding: '32px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
              Industrie & Réseau
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '8px' }}>Grandes Usines</h3>
            <div className="tabular-numbers" style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'IBM Plex Mono, monospace', marginBottom: '16px' }}>
              Sur Mesure
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: 1.5 }}>
              Déploiement multisites, modèles ML dédiés, isolation forest et audits certifiés ISO 50001.
            </p>

            <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 28px 0', fontSize: '13px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={15} color="var(--status-success)" />
                <span>Parc illimité d'équipements & sites</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={15} color="var(--status-success)" />
                <span>Générateur de rapports PDF, DOCX, XLSX, PPTX</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={15} color="var(--status-success)" />
                <span>Accès API REST & intégration SCADA</span>
              </li>
            </ul>

            <button
              onClick={() => handleQuickDemoLogin('Industriel')}
              className="btn-outline"
              style={{ marginTop: 'auto', width: '100%' }}
            >
              Accéder à la Console Industrielle
            </button>
          </div>
        </div>
      </section>

      {/* 9. ACCÈS ANTICIPÉ (Capture email sobre) */}
      <section style={{ backgroundColor: 'var(--bg-surface)', padding: '56px 24px', borderTop: '1px solid var(--border-color)' }}>
        <div style={{ maxWidth: '640px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: '26px', fontWeight: 800, marginBottom: '12px' }}>
            Rejoignez les premiers sites pilotes à Abidjan
          </h2>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: 1.5 }}>
            Recevez les mises à jour des modèles ML et soyez informé de l'ouverture du programme de capteurs connectés.
          </p>

          {!newsletterSent ? (
            <form onSubmit={handleNewsletterSubmit} style={{ display: 'flex', gap: '10px', maxWidth: '460px', margin: '0 auto' }}>
              <input
                type="email"
                placeholder="Votre adresse email professionnelle"
                value={newsletterEmail}
                onChange={(e) => setNewsletterEmail(e.target.value)}
                required
                className="input-standard"
                style={{ flex: 1 }}
              />
              <button type="submit" className="btn-cta" style={{ whiteSpace: 'nowrap' }}>
                S'inscrire
              </button>
            </form>
          ) : (
            <div style={{ padding: '12px 20px', backgroundColor: 'var(--status-success-bg)', color: 'var(--status-success)', borderRadius: 'var(--radius-md)', display: 'inline-flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: 700 }}>
              <CheckCircle2 size={16} />
              <span>Votre adresse a été enregistrée. Merci.</span>
            </div>
          )}
        </div>
      </section>

      {/* 10. FOOTER */}
      <footer style={{ backgroundColor: 'var(--bg-card)', borderTop: '1px solid var(--border-color)', padding: '48px 24px 32px 24px', fontSize: '13px', color: 'var(--text-secondary)' }}>
        <div style={{ maxWidth: '1240px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '32px', marginBottom: '40px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <Image src="/NouankanyAI.png" alt="Logo" width={28} height={28} style={{ objectFit: 'contain' }} />
              <span style={{ fontSize: '16px', fontWeight: 800, fontFamily: 'Space Grotesk, sans-serif', color: 'var(--text-primary)' }}>
                NouanKanyAI
              </span>
            </div>
            <p style={{ lineHeight: 1.5, color: 'var(--text-muted)' }}>
              Plateforme d'optimisation énergétique et de prédiction de charge en Côte d'Ivoire.
            </p>
          </div>

          <div>
            <h4 style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-primary)', marginBottom: '14px' }}>
              Produit
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <a href="#pour-qui" style={{ color: 'inherit' }}>Ménages</a>
              <a href="#pour-qui" style={{ color: 'inherit' }}>PME & Commerces</a>
              <a href="#pour-qui" style={{ color: 'inherit' }}>Industrie</a>
              <a href="#formules" style={{ color: 'inherit' }}>Grille Tarifaire CIE</a>
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-primary)', marginBottom: '14px' }}>
              Technologie
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <span>XGBoost v2.0</span>
              <span>Isolation Forest</span>
              <span>Google Gemini AI</span>
              <span>FastAPI & Next.js 15</span>
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-primary)', marginBottom: '14px' }}>
              Origine & Cadre
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', color: 'var(--text-muted)' }}>
              <span>FORPRODE IA 2026</span>
              <span>Tech Talent Accelerator</span>
              <span>GIZ Côte d'Ivoire</span>
              <span>Abidjan, Côte d'Ivoire</span>
            </div>
          </div>
        </div>

        <div style={{ maxWidth: '1240px', margin: '0 auto', borderTop: '1px solid var(--border-color)', paddingTop: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>
          <div>© 2026 NouanKanyAI. Tous droits réservés.</div>
          <div style={{ display: 'flex', gap: '20px' }}>
            <span>Mentions Légales</span>
            <span>Confidentialité</span>
            <span>Conditions d'Utilisation</span>
          </div>
        </div>
      </footer>

      {/* AUTH MODAL */}
      {isAuthModalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.6)',
            backdropFilter: 'blur(4px)',
            zIndex: 99990,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
          onClick={() => setIsAuthModalOpen(false)}
        >
          <div
            className="card-standard"
            style={{
              width: '100%',
              maxWidth: '460px',
              backgroundColor: 'var(--bg-elevated)',
              boxShadow: 'var(--shadow-dropdown)',
              borderRadius: 'var(--radius-lg)',
              padding: '32px',
              animation: 'fadeIn 0.2s ease-out forwards',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
              <div>
                <h3 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  {authMode === 'login' ? 'Connexion à votre espace' : 'Créer un compte NouanKanyAI'}
                </h3>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  {authMode === 'login'
                    ? 'Accédez à votre tableau de bord énergétique.'
                    : 'Rejoignez le réseau d\'optimisation CIE.'}
                </p>
              </div>
              <button
                onClick={() => setIsAuthModalOpen(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Accès Démo Rapide */}
            <div style={{ padding: '12px', backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '20px' }}>
              <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                ⚡ Accès Immédiat sans mot de passe :
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '6px' }}>
                <button onClick={() => handleQuickDemoLogin('Ménage')} className="btn-ghost" style={{ fontSize: '11px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-card)' }}>
                  🏠 Ménage
                </button>
                <button onClick={() => handleQuickDemoLogin('PME')} className="btn-ghost" style={{ fontSize: '11px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-card)' }}>
                  🏪 PME
                </button>
                <button onClick={() => handleQuickDemoLogin('Industriel')} className="btn-ghost" style={{ fontSize: '11px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-card)' }}>
                  🏭 Industrie
                </button>
                <button onClick={() => handleQuickDemoLogin('Admin')} className="btn-ghost" style={{ fontSize: '11px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-card)' }}>
                  ⚙️ Admin MLOps
                </button>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--border-color)' }} />
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>OU PAR EMAIL</span>
              <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--border-color)' }} />
            </div>

            <form onSubmit={handleAuthSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {authMode === 'register' && (
                <div>
                  <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    Nom complet ou Entreprise
                  </label>
                  <input
                    type="text"
                    placeholder="Ex: Entreprise Adjamé SA"
                    value={nom}
                    onChange={(e) => setNom(e.target.value)}
                    className="input-standard"
                    required
                  />
                </div>
              )}

              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Adresse Email
                </label>
                <input
                  type="email"
                  placeholder="contact@entreprise.ci"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-standard"
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Mot de passe
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-standard"
                  required
                />
              </div>

              {authMode === 'register' && (
                <div>
                  <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    Profil d'activité
                  </label>
                  <select
                    value={typeCompte}
                    onChange={(e) => setTypeCompte(e.target.value)}
                    className="input-standard"
                  >
                    <option value="Industriel">Industrie & Grande Usine</option>
                    <option value="Entreprise">PME, Commerce ou Restaurant</option>
                    <option value="Particulier">Ménage & Particulier</option>
                  </select>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="btn-cta"
                style={{ width: '100%', marginTop: '6px' }}
              >
                {loading
                  ? 'Vérification...'
                  : authMode === 'login'
                  ? 'Accéder au Tableau de Bord'
                  : 'Créer mon Espace'}
              </button>
            </form>

            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              <button
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', fontSize: '13px', cursor: 'pointer', textDecoration: 'underline' }}
              >
                {authMode === 'login'
                  ? "Vous n'avez pas de compte ? S'inscrire"
                  : "Déjà un compte ? Se connecter"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
