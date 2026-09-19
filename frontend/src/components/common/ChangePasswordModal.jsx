import { useState } from 'react';
import { X, KeyRound } from 'lucide-react';
import api from '../../utils/api';

/**
 * Ubah password untuk SEMUA role (admin/guru/siswa). Verifikasi cukup
 * dengan mencocokkan email akun -- kalau email benar, password baru
 * langsung berlaku (tanpa perlu password lama).
 */
export default function ChangePasswordModal({ userEmail, onClose }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirm) {
      setError('Konfirmasi password tidak sama.');
      return;
    }

    setSaving(true);
    try {
      await api.post('/auth/change-password/', { email, new_password: password });
      setSuccess(true);
    } catch (err) {
      setError(
        typeof err.response?.data === 'object'
          ? Object.values(err.response.data).flat().join(' ')
          : 'Gagal mengubah password.'
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4" onClick={onClose}>
      <div className="card w-full max-w-sm p-6" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-surface-900 flex items-center gap-2">
            <KeyRound className="w-5 h-5 text-primary-600" /> Ubah Password
          </h2>
          <button onClick={onClose}><X className="w-5 h-5 text-surface-400" /></button>
        </div>

        {success ? (
          <div className="text-center py-4">
            <p className="text-green-600 font-semibold mb-4">Password berhasil diubah.</p>
            <button onClick={onClose} className="btn-primary w-full">Tutup</button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="label">Email Anda ({userEmail})</label>
              <input
                type="email"
                className="input"
                placeholder="Ketik ulang email Anda untuk verifikasi"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="label">Password Baru</label>
              <input type="password" className="input" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            <div>
              <label className="label">Konfirmasi Password Baru</label>
              <input type="password" className="input" required value={confirm} onChange={(e) => setConfirm(e.target.value)} />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button type="submit" disabled={saving} className="btn-primary w-full">
              {saving ? 'Menyimpan...' : 'Simpan Password Baru'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
