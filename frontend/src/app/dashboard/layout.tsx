'use client';

import React, { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import {
  LayoutDashboard,
  Factory,
  Plug,
  Bot,
  Receipt,
  Settings,
  LogOut,
  Menu,
  X,
  Search,
  ChevronDown,
  Sparkles,
  Command,
  HelpCircle,
} from 'lucide-react';
import { supabase } from '@/lib/supabase';
import { MLHealthBadge } from '@/components/ml';
import { LevelSelector, UserLevel } from '@/components/ui/LevelSelector';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { CommandPalette } from '@/components/ui/CommandPalette';
import { CopilotWidget } from '@/components/ui/CopilotWidget';
import { ProvenanceBadge } from '@/components/ui/ProvenanceBadge';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  const [user, setUser] = useState<any>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [currentLevel, setCurrentLevel] = useState<UserLevel>('amateur');
  const [activeProfile, setActiveProfile] = useState<string>('PME');

  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  useEffect(() => {
    const savedLevel = localStorage.getItem('nouankanyai_level') as UserLevel | null;
    if (savedLevel) setCurrentLevel(savedLevel);

    const savedProfile = localStorage.getItem('nouankanyai_profile');
    if (savedProfile) setActiveProfile(savedProfile);
  }, []);

  const handleLevelChange = (level: UserLevel) => {
    setCurrentLevel(level);
    localStorage.setItem('nouankanyai_level', level);
  };

  const handleProfileSwitch = (profile: string) => {
    setActiveProfile(profile);
    localStorage.setItem('nouankanyai_profile', profile);

    const defaultLevels: Record<string, UserLevel> = {
      Ménage: 'debutant',
      PME: 'amateur',
      Industriel: 'technique',
      Admin: 'technique',
    };
    const nextLevel = defaultLevels[profile] || 'amateur';
    setCurrentLevel(nextLevel);
    localStorage.setItem('nouankanyai_level', nextLevel);

    if (profile === 'Admin') {
      router.push('/dashboard/admin');
    }
  };

  const handleLogout = async () => {
    localStorage.removeItem('mockUser');
    localStorage.removeItem('nouankanyai_profile');
    if (supabase) {
      await supabase.auth.signOut();
    }
    router.push('/');
  };

  useEffect(() => {
    const checkUser = async () => {
      const mockUser = localStorage.getItem('mockUser');
      if (mockUser) {
        setUser(JSON.parse(mockUser));
        return;
      }

      if (supabase) {
        const { data: { session } } = await supabase.auth.getSession();
        if (session && session.user) {
          setUser({
            nom: session.user.user_metadata?.nom || session.user.email?.split('@')[0],
            email: session.user.email,
            type_compte: session.user.user_metadata?.role || 'Industriel',
          });
          return;
        }
      }

      // Default demo user if accessed directly
      const fallbackUser = {
        nom: 'Responsable Énergie',
        email: 'contact@nouankanyai.ci',
        type_compte: 'PME',
      };
      setUser(fallbackUser);
      localStorage.setItem('mockUser', JSON.stringify(fallbackUser));
    };

    checkUser();
  }, [router]);

  if (!user) return null;

  const navItems = [
    { href: '/dashboard', label: 'Tableau de Bord', icon: LayoutDashboard, exact: true },
    { href: '/dashboard/sites', label: 'Sites & Lieux', icon: Factory },
    { href: '/dashboard/appareils', label: 'Équipements', icon: Plug },
    { href: '/dashboard/predictions', label: 'Assistant & Inférence', icon: Bot },
    { href: '/dashboard/facturation', label: 'Facturation & Gain-Share', icon: Receipt },
    { href: '/dashboard/admin', label: 'Console Admin MLOps', icon: Settings },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            backdropFilter: 'blur(3px)',
            zIndex: 999,
          }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        style={{
          width: '260px',
          backgroundColor: 'var(--bg-card)',
          borderRight: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 1000,
          position: sidebarOpen ? 'fixed' : 'relative',
          top: 0,
          bottom: 0,
          left: 0,
          transition: 'transform 0.25s ease',
          transform: sidebarOpen ? 'translateX(0)' : undefined,
        }}
        className={sidebarOpen ? 'sidebar-open' : ''}
      >
        {/* Brand */}
        <div style={{ padding: '20px 22px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div
            onClick={() => router.push('/')}
            style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}
          >
            <Image
              src="/NouankanyAI.png"
              alt="Logo"
              width={34}
              height={34}
              style={{ objectFit: 'contain' }}
            />
            <div>
              <div style={{ fontSize: '16px', fontWeight: 800, fontFamily: 'Space Grotesk, sans-serif', color: 'var(--text-primary)' }}>
                NouanKanyAI
              </div>
              <div style={{ fontSize: '9px', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.06em' }}>
                SUPERVISION ÉNERGIE
              </div>
            </div>
          </div>

          <button
            onClick={() => setSidebarOpen(false)}
            className="sidebar-close-btn"
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'none' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Profil Selector Dropdown */}
        <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border-subtle)' }}>
          <label style={{ display: 'block', fontSize: '10px', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '6px' }}>
            Profil d'exploitation
          </label>
          <select
            value={activeProfile}
            onChange={(e) => handleProfileSwitch(e.target.value)}
            className="input-standard"
            style={{ minHeight: '34px', padding: '4px 8px', fontSize: '12px', fontWeight: 600, backgroundColor: 'var(--bg-surface)' }}
          >
            <option value="Ménage">🏠 Profil Ménage (Débutant)</option>
            <option value="PME">🏪 Profil PME & Commerce (Amateur)</option>
            <option value="Industriel">🏭 Profil Industrie (Technique)</option>
            <option value="Admin">⚙️ Console Admin MLOps</option>
          </select>
        </div>

        {/* Navigation Section */}
        <div style={{ padding: '16px 14px 8px 14px', fontSize: '10px', fontWeight: 800, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
          Menu Principal
        </div>

        <nav style={{ flex: 1, padding: '0 12px', display: 'flex', flexDirection: 'column', gap: '3px' }}>
          {navItems.map(({ href, label, icon: Icon, exact }) => {
            const isActive = exact ? pathname === href : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '13px',
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                  backgroundColor: isActive ? 'var(--bg-surface)' : 'transparent',
                  border: isActive ? '1px solid var(--border-color)' : '1px solid transparent',
                  transition: 'all 0.15s ease',
                }}
              >
                <Icon size={16} color={isActive ? 'var(--accent-cta)' : 'currentColor'} />
                <span>{label}</span>
              </Link>
            );
          })}
        </nav>

        {/* User Info & Footer */}
        <div
          style={{
            padding: '16px 18px',
            borderTop: '1px solid var(--border-color)',
            backgroundColor: 'var(--bg-surface)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: 'var(--accent-cta)',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 800,
                fontSize: '13px',
                flexShrink: 0,
              }}
            >
              {user.nom ? user.nom.charAt(0).toUpperCase() : 'U'}
            </div>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: '13px', fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: 'var(--text-primary)' }}>
                {user.nom}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                {activeProfile}
              </div>
            </div>
          </div>

          <button
            onClick={handleLogout}
            title="Se déconnecter"
            className="btn-ghost"
            style={{ padding: '6px' }}
          >
            <LogOut size={16} />
          </button>
        </div>
      </aside>

      {/* Main Container */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        {/* Top Header */}
        <header
          style={{
            height: '64px',
            backgroundColor: 'var(--bg-card)',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 32px',
            flexShrink: 0,
            gap: '16px',
          }}
        >
          {/* Mobile hamburger */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="btn-ghost mobile-menu-btn"
            style={{ display: 'none', padding: '6px' }}
            aria-label="Ouvrir le menu"
          >
            <Menu size={20} />
          </button>

          {/* Quick Search & Command Palette trigger */}
          <div
            onClick={() => setIsCommandPaletteOpen(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-full)',
              padding: '6px 14px',
              width: '320px',
              maxWidth: '100%',
              cursor: 'pointer',
              color: 'var(--text-muted)',
              fontSize: '13px',
            }}
          >
            <Search size={14} />
            <span style={{ flex: 1 }}>Recherche rapide (Ctrl+K)...</span>
            <kbd style={{ fontSize: '10px', padding: '2px 6px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '4px', fontWeight: 700 }}>
              ⌘K
            </kbd>
          </div>

          {/* Right Header items */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <LevelSelector currentLevel={currentLevel} onSelectLevel={handleLevelChange} size="sm" />
            <ThemeToggle />
            <MLHealthBadge showDetails={true} />
          </div>
        </header>

        {/* Scrollable Page Content */}
        <main
          style={{
            flex: 1,
            padding: '32px',
            overflowY: 'auto',
            backgroundColor: 'var(--bg-primary)',
          }}
        >
          <div style={{ maxWidth: '1240px', margin: '0 auto' }}>
            {children}
          </div>
        </main>
      </div>

      {/* Global Command Palette */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onSelectLevel={handleLevelChange}
      />

      {/* Floating Copilot Widget */}
      <CopilotWidget />
    </div>
  );
}
