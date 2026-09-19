import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SiswaLayout from '../../components/siswa/SiswaLayout';
import api from '../../utils/api';
import { SkeletonRows } from '../../components/common/Loading';
import { KeyRound, X, CheckCircle2 } from 'lucide-react';

export default function SiswaUjianList() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showToken, setShowToken] = useState(false);
  const [token, setToken] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const load = () => {
    setLoading(true);
    api.get('/ujian/tersedia/').then(({ data }) => setList(data)).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleMasuk = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const { data } = await api.post('/ujian/masuk/', { token: token.toUpperCase() });
      navigate(`/siswa/ujian/${data.ujian.id}`, { state: { token: token.toUpperCase() } });
    } catch (err) {
      setError(err.response?.data?.detail || 'Token tidak valid.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <SiswaLayout title="Ujian Tersedia">
      <div className="flex items-center justify-between mb-5">
        <p className="text-sm text-surface-500">Ujian untuk kelas & jurusan Anda.</p>
        <button onClick={() => setShowToken(true)} className="btn-primary flex items-center gap-2">
          <KeyRound className="w-4 h-4" /> Masukkan Token
        </button>
      </div>

      {showToken && (
        <div className="fixed inset-0 z-40 bg-black/40 flex items-center justify-center p-4" onClick={() => setShowToken(false)}>
          <div className="card w-full max-w-sm p-6" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-surface-900">Masukkan Token Ujian</h2>
              <button onClick={() => setShowToken(false)}><X className="w-5 h-5 text-surface-400" /></button>
            </div>
            <form onSubmit={handleMasuk} className="space-y-4">
              <input
                className="input text-center text-2xl font-mono font-bold tracking-widest uppercase"
                maxLength={5}
                value={token}
                onChange={e => setToken(e.target.value.toUpperCase())}
                placeholder="XXXXX"
                required
                autoFocus
              />
              {error && <p className="text-sm text-red-600">{error}</p>}
              <button type="submit" disabled={submitting || token.length !== 5} className="btn-primary w-full">
                {submitting ? 'Memeriksa...' : 'Masuk Ujian'}
              </button>
            </form>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {loading ? [...Array(2)].map((_, i) => <div key={i} className="card p-5 h-32 animate-pulse" />) : list.map(u => (
          <div key={u.id} className="card p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-semibold uppercase text-primary-600">{u.jenis_ujian}</p>
                <h3 className="font-bold text-surface-900 mt-0.5">{u.nama_ujian}</h3>
              </div>
              {u.sudah_dikerjakan && <span className="badge bg-green-100 text-green-700 gap-1"><CheckCircle2 className="w-3 h-3" /> Selesai</span>}
            </div>
            <p className="text-sm text-surface-500 mt-2">Guru: {u.guru_pembuat}</p>
            <p className="text-sm text-surface-500">{u.jumlah_soal} soal</p>
          </div>
        ))}
        {!loading && list.length === 0 && (
          <p className="text-surface-400 col-span-2 text-center py-8">Belum ada ujian tersedia untuk kelas Anda.</p>
        )}
      </div>
    </SiswaLayout>
  );
}
