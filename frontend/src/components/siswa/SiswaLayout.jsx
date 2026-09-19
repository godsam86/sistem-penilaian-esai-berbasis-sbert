import { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  Home, ClipboardList, History, BarChart2,
  User, LogOut, Bell, ChevronDown, Menu, X, KeyRound
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import ChangePasswordModal from '../common/ChangePasswordModal';
import { SCHOOL_NAME, SCHOOL_LOGO_URL } from '../../branding';

// Profil dipindah ke dropdown navbar saja -- tidak lagi jadi menu sidebar.
const NAV = [
  { to: '/siswa/dashboard', label: 'Beranda',        icon: Home,          exact: true },
  { to: '/siswa/ujian',     label: 'Ujian Tersedia',  icon: ClipboardList, exact: false },
  { to: '/siswa/riwayat',   label: 'Riwayat Ujian',   icon: History,       exact: false },
  { to: '/siswa/hasil',     label: 'Hasil Ujian',     icon: BarChart2,     exact: false },
];

export default function SiswaLayout({ children, title }) {
  const { user, logout } = useAuth();
  const navigate  = useNavigate();
  const location  = useLocation();
  const [sideOpen,  setSideOpen]  = useState(false);
  const [dropOpen,  setDropOpen]  = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const dropRef  = useRef(null);
  const notifRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (dropRef.current  && !dropRef.current.contains(e.target))  setDropOpen(false);
      if (notifRef.current && !notifRef.current.contains(e.target)) setNotifOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (item) => {
    if (item.exact) return location.pathname === item.to;
    return location.pathname.startsWith(item.to);
  };

  const initials = user?.nama
    ? user.nama.split(' ').slice(0, 2).map(n => n[0]).join('').toUpperCase()
    : 'S';

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {showChangePassword && (
        <ChangePasswordModal userEmail={user?.email} onClose={() => setShowChangePassword(false)} />
      )}
      {sideOpen && (
        <div className="fixed inset-0 bg-black/40 z-30 lg:hidden"
          onClick={() => setSideOpen(false)} />
      )}

      {/* ── SIDEBAR ──────────────────────────────────────── */}
      <aside className={`
        fixed top-0 left-0 h-full w-64 bg-white z-40
        flex flex-col shadow-xl transition-transform duration-300
        ${sideOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:shadow-none
      `}>
        <div className="flex items-center gap-3 px-5 py-5 border-b border-gray-100">
          <img src={SCHOOL_LOGO_URL} alt="Logo" className="w-10 h-10 rounded-xl object-cover shadow" />
          <div>
            <p className="text-sm font-bold text-gray-900 leading-tight">{SCHOOL_NAME}</p>
            <p className="text-xs text-green-600 font-medium">Portal Siswa</p>
          </div>
          <button className="ml-auto lg:hidden text-gray-400 hover:text-gray-600"
            onClick={() => setSideOpen(false)}>
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV.map(item => {
            const active = isActive(item);
            return (
              <NavLink key={item.to} to={item.to}
                end={item.exact}
                onClick={() => setSideOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium
                  transition-all duration-150
                  ${active
                    ? 'bg-green-50 text-green-700 shadow-sm'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}
                `}>
                <div className={`p-1.5 rounded-lg ${active ? 'bg-green-600' : 'bg-gray-100'}`}>
                  <item.icon className={`w-4 h-4 ${active ? 'text-white' : 'text-gray-500'}`} />
                </div>
                {item.label}
                {active && <div className="ml-auto w-1.5 h-5 bg-green-600 rounded-full" />}
              </NavLink>
            );
          })}
        </nav>

        <div className="mx-3 mb-4 p-4 bg-gradient-to-br from-green-600 to-green-700 rounded-2xl text-white">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-base">✦</span>
            <p className="text-xs font-bold">Tetap Semangat!</p>
          </div>
          <p className="text-xs opacity-90 leading-relaxed">
            Kerjakan ujian dengan jujur dan maksimal untuk hasil terbaikmu.
          </p>
          {user?.nama && (
            <p className="mt-2 text-xs font-semibold opacity-80">
              Semangat, {user.nama.split(' ')[0]}! 👋
            </p>
          )}
        </div>
      </aside>

      {/* ── MAIN AREA ─────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-20 bg-white border-b border-gray-100 shadow-sm">
          <div className="flex items-center gap-3 px-4 py-3">
            <button className="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100"
              onClick={() => setSideOpen(true)}>
              <Menu className="w-5 h-5" />
            </button>

            <h1 className="text-base font-bold text-gray-900 hidden sm:block">{title}</h1>

            <div className="ml-auto flex items-center gap-2">
              <div className="relative" ref={notifRef}>
                <button onClick={() => setNotifOpen(v => !v)}
                  className="relative p-2 rounded-xl text-gray-500 hover:bg-gray-100 transition-all">
                  <Bell className="w-5 h-5" />
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-green-500 rounded-full" />
                </button>
                {notifOpen && (
                  <div className="absolute right-0 top-12 w-72 bg-white rounded-2xl shadow-xl border border-gray-100 p-4 z-50">
                    <p className="text-sm font-bold text-gray-800 mb-3">Notifikasi</p>
                    <div className="flex flex-col items-center py-4 text-gray-400">
                      <Bell className="w-8 h-8 mb-2 opacity-30" />
                      <p className="text-xs">Belum ada notifikasi</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="relative" ref={dropRef}>
                <button onClick={() => setDropOpen(v => !v)}
                  className="flex items-center gap-2 pl-1 pr-3 py-1.5 rounded-xl hover:bg-gray-100 transition-all">
                  {user?.photo_url
                    ? <img src={user.photo_url} alt="foto"
                        className="w-8 h-8 rounded-full object-cover border-2 border-green-200" />
                    : <div className="w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center text-xs font-bold">
                        {initials}
                      </div>
                  }
                  <div className="hidden sm:block text-left">
                    <p className="text-xs font-bold text-gray-900 leading-tight">
                      {user?.nama || 'Siswa'}
                    </p>
                    <p className="text-xs text-gray-500">
                      Kelas {user?.kelas} - {user?.jurusan}
                    </p>
                  </div>
                  <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${dropOpen ? 'rotate-180' : ''}`} />
                </button>

                {dropOpen && (
                  <div className="absolute right-0 top-12 w-56 bg-white rounded-2xl shadow-xl border border-gray-100 p-2 z-50">
                    <div className="px-3 py-2 mb-1">
                      <p className="text-xs font-bold text-gray-900">{user?.nama}</p>
                      <p className="text-xs text-gray-500">{user?.email}</p>
                    </div>
                    <div className="border-t border-gray-100 pt-1">
                      <NavLink to="/siswa/profil"
                        onClick={() => setDropOpen(false)}
                        className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-gray-700 hover:bg-gray-50">
                        <User className="w-4 h-4" /> Profil Saya
                      </NavLink>
                      <button onClick={() => { setDropOpen(false); setShowChangePassword(true); }}
                        className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-gray-700 hover:bg-gray-50">
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
          </div>
        </header>

        <main className="flex-1 p-4 sm:p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
