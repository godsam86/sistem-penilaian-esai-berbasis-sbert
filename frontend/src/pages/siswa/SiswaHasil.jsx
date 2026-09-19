import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import SiswaLayout from '../../components/siswa/SiswaLayout';
import api from '../../utils/api';

export default function SiswaHasil() {
  const { ujianId } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/penilaian/nilai-ujian/${ujianId}/`)
      .then(({ data }) => setData(data))
      .catch(err => setError(err.response?.data?.detail || 'Hasil belum tersedia.'))
      .finally(() => setLoading(false));
  }, [ujianId]);

  return (
    <SiswaLayout title="Hasil Ujian">
      {loading && <p className="text-surface-400 text-center py-10">Memuat...</p>}
      {error && <div className="card p-8 text-center text-amber-600">{error}</div>}
      {data && (
        <div className="space-y-4">
          <div className="card p-6 text-center bg-primary-50 border-primary-200">
            <p className="text-sm text-primary-700 font-semibold">Nilai Akhir</p>
            <p className="text-5xl font-extrabold text-primary-700 mt-1">{data.nilai_akhir}</p>
          </div>
          {data.detail_per_soal.map((d, i) => (
            <div key={d.id} className="card p-5">
              <p className="font-semibold text-surface-800 mb-1">Soal {i + 1}</p>
              <p className="text-surface-700 mb-2">{d.pertanyaan}</p>
              <p className="text-sm text-surface-500 mb-2 italic">Jawaban Anda: {d.jawaban_teks || '(kosong)'}</p>
              <div className="flex items-center justify-between">
                <span className="badge bg-primary-100 text-primary-700">Skor: {d.final_score?.toFixed(2) ?? '-'}</span>
              </div>
              <p className="text-sm text-surface-600 mt-2">{d.feedback}</p>
            </div>
          ))}
        </div>
      )}
    </SiswaLayout>
  );
}
