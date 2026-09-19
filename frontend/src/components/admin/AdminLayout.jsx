import { useState, useRef, useEffect } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import ChangePasswordModal from '../common/ChangePasswordModal';
import { SCHOOL_NAME, SCHOOL_LOGO_URL } from '../../branding';
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  BarChart3,
  LogOut,
  ChevronRight,
  ChevronDown,
  Menu,
  X,
  Building2,
  User,
  KeyRound,
  Shield,
} from 'lucide-react';

const navItems = [
  { to: '/admin/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/admin/akun', icon: Shield, label: 'Akun Admin' },
  { to: '/admin/guru', icon: Users, label: 'Guru' },
  { to: '/admin/siswa', icon: GraduationCap, label: 'Siswa' },
  { to: '/admin/master-data', icon: Building2, label: 'Kelas & Jurusan' },
  { to: '/admin/penilaian', icon: BarChart3, label: 'Penilaian' },
];

export default function AdminLayout({ children, title }) {
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

  const initials = user?.nama?.split(' ').slice(0, 2).map((n) => n[0]).join('').toUpperCase() || 'A';

  return (
    <div className="flex min-h-screen bg-slate-100">
      {showChangePassword && (
        <ChangePasswordModal userEmail={user?.email} onClose={() => setShowChangePassword(false)} />
      )}

      {sideOpen && (
        <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={() => setSideOpen(false)} />
      )}
      <aside className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col bg-slate-900 text-slate-100 transition-transform duration-300 lg:static lg:translate-x-0 ${sideOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="border-b border-slate-800 px-5 py-6">
          <div className="flex items-center gap-3">
            <img src={SCHOOL_LOGO_URL} alt="Logo" className="w-11 h-11 rounded-xl object-cover shadow-lg" />
            <div>
              <p className="text-sm font-bold leading-tight">{SCHOOL_NAME}</p>
              <p className="text-xs text-slate-400">Panel Admin</p>
            </div>
            <button onClick={() => setSideOpen(false)} className="ml-auto p-1 text-slate-400 hover:text-white lg:hidden" aria-label="Tutup menu">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <nav className="p-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => {
            const active = location.pathname === to;
            return (
                <NavLink
                key={to}
                to={to}
                  onClick={() => setSideOpen(false)}
                className={`flex items-center justify-between gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  active
                    ? 'bg-violet-600 text-white shadow-lg shadow-violet-600/20'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <span className="flex items-center gap-3">
                  <Icon className="w-4 h-4" />
                  {label}
                </span>
                {active && <ChevronRight className="w-4 h-4" />}
              </NavLink>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 min-w-0">
        <header className="border-b border-slate-200 bg-white/90 backdrop-blur-sm sticky top-0 z-20">
          <div className="flex items-center justify-between gap-3 px-4 py-3 sm:px-6 sm:py-4">
            <div>
              <div className="flex items-center gap-3">
                <button onClick={() => setSideOpen(true)} className="p-2 text-slate-500 hover:bg-slate-100 rounded-lg lg:hidden" aria-label="Buka menu">
                  <Menu className="w-5 h-5" />
                </button>
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-violet-600 font-semibold">Admin</p>
                  <h1 className="text-lg sm:text-2xl font-bold text-slate-900 mt-1">{title}</h1>
                </div>
              </div>
            </div>

            {/* Satu-satunya jalan ke Profil / Ubah Password / Keluar -- tidak ada lagi di sidebar */}
            <div className="relative" ref={dropRef}>
              <button
                onClick={() => setDropOpen((v) => !v)}
                className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 transition-all"
              >
                <div className="w-8 h-8 rounded-full bg-violet-600 text-white flex items-center justify-center text-xs font-bold">
                  {initials}
                </div>
                <span className="hidden sm:block text-sm font-semibold text-slate-800">{user?.nama || 'Admin'}</span>
                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${dropOpen ? 'rotate-180' : ''}`} />
              </button>

              {dropOpen && (
                <div className="absolute right-0 top-12 w-56 bg-white rounded-2xl shadow-xl border border-slate-100 p-2 z-50">
                  <div className="px-3 py-2 mb-1">
                    <p className="text-xs font-bold text-slate-900">{user?.nama}</p>
                    <p className="text-xs text-slate-500">{user?.email}</p>
                  </div>
                  <div className="border-t border-slate-100 pt-1">
                    <NavLink to="/admin/profil" onClick={() => setDropOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-slate-700 hover:bg-slate-50">
                      <User className="w-4 h-4" /> Lihat Profil
                    </NavLink>
                    <button onClick={() => { setDropOpen(false); setShowChangePassword(true); }}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-slate-700 hover:bg-slate-50">
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

        <div className="p-4 sm:p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
