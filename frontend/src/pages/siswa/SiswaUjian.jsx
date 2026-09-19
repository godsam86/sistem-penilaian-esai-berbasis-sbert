import { useEffect, useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import SiswaLayout from '../../components/siswa/SiswaLayout';
import api from '../../utils/api';
import { LoadingOverlay } from '../../components/common/Loading';
import { Send, CheckCircle2 } from 'lucide-react';

export default function SiswaUjian() {
  const { ujianId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [token, setToken] = useState(location.state?.token || sessionStorage.getItem(`token-ujian-${ujianId}`) || '');
  const [data, setData] = useState(null);
  const [jawabanText, setJawabanText] = useState({});
  const [loading, setLoading] = useState(true);
  const [submittingId, setSubmittingId] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) {
      navigate('/siswa/ujian');
      return;
    }
    sessionStorage.setItem(`token-ujian-${ujianId}`, token);
    api.post('/ujian/masuk/', { token })
      .then(({ data }) => setData(data))
      .catch(() => { navigate('/siswa/ujian'); })
      .finally(() => setLoading(false));
  }, [ujianId]);

  const handleSubmitSoal = async (soalId) => {
    setError('');
    setSubmittingId(soalId);
    try {
      await api.post('/jawaban/submit/', {
        ujian_id: ujianId,
        soal_id: soalId,
        token,
        jawaban_teks: jawabanText[soalId] || '',
      });
      setData(prev => ({
        ...prev,
        soal: prev.soal.map(s => s.id === soalId ? { ...s, sudah_dijawab: true } : s),
      }));
    } catch (err) {
      setError(err.response?.data?.detail || 'Gagal mengirim jawaban.');
    } finally {
      setSubmittingId(null);
    }
  };

  if (loading) return <SiswaLayout title="Ujian"><p className="text-surface-400 text-center py-10">Memuat...</p></SiswaLayout>;
  if (!data) return null;

  const semuaSelesai = data.soal.every(s => s.sudah_dijawab);

  return (
    <SiswaLayout title={data.ujian.nama_ujian}>
      <LoadingOverlay show={!!submittingId} message="Menilai jawaban Anda..." sub="Mohon tunggu sebentar" />

      {error && <div className="mb-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">{error}</div>}

      <div className="space-y-4">
        {data.soal.map((s, idx) => (
          <div key={s.id} className="card p-5">
            <div className="flex items-center justify-between mb-2">
              <p className="font-semibold text-surface-800">Soal {idx + 1}</p>
              {s.sudah_dijawab && <span className="badge bg-green-100 text-green-700 gap-1"><CheckCircle2 className="w-3 h-3" /> Terkirim</span>}
            </div>
            <p className="text-surface-700 mb-3">{s.pertanyaan}</p>
            {s.sudah_dijawab ? (
              <p className="text-sm text-surface-400 italic">Jawaban sudah dikirim dan tidak dapat diubah.</p>
            ) : (
              <>
                <textarea
                  className="input min-h-[120px]"
                  placeholder="Tulis jawaban Anda di sini..."
                  value={jawabanText[s.id] || ''}
                  onChange={e => setJawabanText(p => ({ ...p, [s.id]: e.target.value }))}
                />
                <button
                  onClick={() => handleSubmitSoal(s.id)}
                  disabled={submittingId === s.id}
                  className="btn-primary mt-3 flex items-center gap-2"
                >
                  <Send className="w-4 h-4" /> Kirim Jawaban
                </button>
              </>
            )}
          </div>
        ))}
      </div>

      {semuaSelesai && (
        <div className="mt-6 card p-5 text-center bg-green-50 border-green-200">
          <p className="font-semibold text-green-700 mb-3">Semua soal telah dikerjakan.</p>
          <button onClick={() => navigate('/siswa/riwayat')} className="btn-primary">Lihat Riwayat Ujian</button>
        </div>
      )}
    </SiswaLayout>
  );
}
