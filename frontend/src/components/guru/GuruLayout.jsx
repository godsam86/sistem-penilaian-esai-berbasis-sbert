import { useState, useRef, useEffect } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import ChangePasswordModal from '../common/ChangePasswordModal';
import { SCHOOL_NAME, SCHOOL_LOGO_URL } from '../../branding';
import {
  LayoutDashboard, Database, FileText, ClipboardList,
  BarChart3, LogOut, ChevronRight, ChevronDown, Menu, X, User, KeyRound,
} from 'lucide-react';

const navItems = [
  { path: '/guru/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/guru/kb', icon: Database, label: 'Knowledge Base' },
  { path: '/guru/soal', icon: FileText, label: 'Manajemen Soal' },
  { path: '/guru/ujian', icon: ClipboardList, label: 'Manajemen Ujian' },
  { path: '/guru/hasil', icon: BarChart3, label: 'Hasil Penilaian' },
];

export default function GuruLayout({ children, title }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sideOpen, setSideOpen] = useState(false);
  const [dropOpen, setDropOpen] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const dropRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (dropRef.current && !dropRef.current.contains(e.target)) setDropOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initials = user?.nama?.split(' ').slice(0, 2).map((n) => n[0]).join('').toUpperCase() || 'G';

  return (
    <div className="flex h-screen bg-surface-50">
      {showChangePassword && (
        <ChangePasswordModal userEmail={user?.email} onClose={() => setShowChangePassword(false)} />
      )}

      {sideOpen && (
        <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={() => setSideOpen(false)} />
      )}
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-surface-900 transition-transform duration-300 lg:static lg:translate-x-0 ${sideOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="p-6 border-b border-surface-800">
          <div className="flex items-center gap-3">
            <img src={SCHOOL_LOGO_URL} alt="Logo" className="w-10 h-10 rounded-xl object-cover" />
            <button onClick={() => setSideOpen(false)} className="ml-auto p-1 text-surface-400 hover:text-white lg:hidden" aria-label="Tutup menu">
              <X className="w-5 h-5" />
            </button>
            <div>
              <p className="text-white font-bold text-sm leading-tight">{SCHOOL_NAME}</p>
              <p className="text-surface-400 text-xs">Panel Guru</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map(({ path, icon: Icon, label }) => {
            const active = location.pathname === path;
            return (
              <Link
                key={path}
                to={path}
                onClick={() => setSideOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all
                  ${active
                    ? 'bg-primary-600 text-white'
                    : 'text-surface-400 hover:bg-surface-800 hover:text-white'
                  }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {label}
                {active && <ChevronRight className="w-3 h-3 ml-auto" />}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white border-b border-surface-200 px-4 py-3 sm:px-8 sm:py-4 shrink-0">
          <div className="flex items-center gap-3">
            <button onClick={() => setSideOpen(true)} className="p-2 text-surface-500 hover:bg-surface-100 rounded-lg lg:hidden" aria-label="Buka menu">
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg sm:text-xl font-bold text-surface-900">{title}</h1>

            {/* Satu-satunya jalan ke Profil / Ubah Password / Keluar */}
            <div className="relative ml-auto" ref={dropRef}>
              <button
                onClick={() => setDropOpen((v) => !v)}
                className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-xl border border-surface-200 hover:bg-surface-50 transition-all"
              >
                <div className="w-8 h-8 bg-accent-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                  {initials}
                </div>
                <span className="hidden sm:block text-sm font-semibold text-surface-800">{user?.nama || 'Guru'}</span>
                <ChevronDown className={`w-4 h-4 text-surface-400 transition-transform ${dropOpen ? 'rotate-180' : ''}`} />
              </button>

              {dropOpen && (
                <div className="absolute right-0 top-12 w-56 bg-white rounded-2xl shadow-xl border border-surface-100 p-2 z-50">
                  <div className="px-3 py-2 mb-1">
                    <p className="text-xs font-bold text-surface-900">{user?.nama}</p>
                    <p className="text-xs text-surface-500">{user?.email}</p>
                  </div>
                  <div className="border-t border-surface-100 pt-1">
                    <NavLink to="/guru/profil" onClick={() => setDropOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-surface-700 hover:bg-surface-50">
                      <User className="w-4 h-4" /> Lihat Profil
                    </NavLink>
                    <button onClick={() => { setDropOpen(false); setShowChangePassword(true); }}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-surface-700 hover:bg-surface-50">
                      <KeyRound className="w-4 h-4" /> Ubah Password
                    </button>
                    <button onClick={handleLogout}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-red-500 hover:bg-red-50">
                      <LogOut className="w-4 h-4" /> Keluar
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto p-4 sm:p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
