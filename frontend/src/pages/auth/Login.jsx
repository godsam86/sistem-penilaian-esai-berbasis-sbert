import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import api from '../../utils/api';
import { SCHOOL_NAME, SCHOOL_LOGO_URL } from '../../branding';
import { Mail, KeyRound, ArrowLeft, Eye, EyeOff } from 'lucide-react';

/**
 * Bagian 4: SATU form login untuk ketiga role (admin/guru/siswa).
 * Field kedua bernama "credential" -- password untuk admin/guru, NISN
 * untuk siswa. Backend yang menentukan artinya, bukan frontend.
 */
export default function Login() {
  const [form, setForm] = useState({ email: '', credential: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showCredential, setShowCredential] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/auth/login/', form);
      const { access, refresh, user } = res.data;
      login(user, access, refresh);

      if (user.role === 'admin') navigate('/admin/dashboard');
      else if (user.role === 'guru') navigate('/guru/dashboard');
      else navigate('/siswa/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login gagal. Periksa kembali data Anda.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-surface-900 to-primary-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Link to="/" className="flex items-center gap-2 text-surface-400 hover:text-white mb-8 transition-colors text-sm">
          <ArrowLeft className="w-4 h-4" /> Kembali ke beranda
        </Link>

        <div className="card p-8 bg-surface-800/80 border-surface-700">
          <div className="text-center mb-8">
            <img src={SCHOOL_LOGO_URL} alt="Logo" className="w-14 h-14 rounded-2xl object-cover mx-auto mb-4" />
            <h1 className="text-2xl font-extrabold text-white">Masuk</h1>
            <p className="text-surface-400 text-sm mt-1">{SCHOOL_NAME}</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label text-surface-300">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" />
                <input
                  type="email"
                  className="input pl-10 bg-surface-700 border-surface-600 text-white placeholder:text-surface-500 focus:ring-primary-500"
                  value={form.email}
                  onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
                  required
                  autoFocus
                />
              </div>
            </div>

            <div>
              <label className="label text-surface-300">Password / NISN</label>
              <p className="text-surface-500 text-xs mb-1.5">Guru &amp; admin: password. Siswa: NISN.</p>
              <div className="relative">
                <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" />
                <input
                  type={showCredential ? 'text' : 'password'}
                  className="input pl-10 pr-10 bg-surface-700 border-surface-600 text-white placeholder:text-surface-500 focus:ring-primary-500"
                  value={form.credential}
                  onChange={e => setForm(p => ({ ...p, credential: e.target.value }))}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowCredential(p => !p)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-500 hover:text-surface-300"
                >
                  {showCredential ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="px-4 py-3 bg-red-900/30 border border-red-700/50 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full justify-center flex items-center gap-2 py-3">
              {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : null}
              {loading ? 'Memproses...' : 'Masuk'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
