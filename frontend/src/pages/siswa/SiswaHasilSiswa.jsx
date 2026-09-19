import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SiswaLayout from '../../components/siswa/SiswaLayout';
import api from '../../utils/api';
import { SkeletonCard } from '../../components/common/Loading';

/** Ringkasan hasil SEMUA ujian yang sudah dipublikasikan (bukan per-ujian). */
export default function SiswaHasilSiswa() {
  const [ujianList, setUjianList] = useState([]);
  const [nilaiMap, setNilaiMap] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/ujian/tersedia/').then(async ({ data }) => {
      setUjianList(data);
      const results = await Promise.allSettled(
        data.map(u => api.get(`/penilaian/nilai-ujian/${u.id}/`))
      );
      const map = {};
      results.forEach((r, i) => {
        if (r.status === 'fulfilled') map[data[i].id] = r.value.data.nilai_akhir;
      });
      setNilaiMap(map);
      setLoading(false);
    });
  }, []);

  const publikasi = ujianList.filter(u => u.id in nilaiMap);

  return (
    <SiswaLayout title="Hasil Ujian Saya">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? [...Array(3)].map((_, i) => <SkeletonCard key={i} />) : publikasi.map(u => (
          <Link to={`/siswa/hasil/${u.id}`} key={u.id} className="card p-5 hover:shadow-md transition-shadow">
            <p className="text-xs font-semibold uppercase text-primary-600">{u.jenis_ujian}</p>
            <h3 className="font-bold text-surface-900 mt-0.5">{u.nama_ujian}</h3>
            <p className="text-3xl font-extrabold text-primary-700 mt-3">{nilaiMap[u.id]}</p>
          </Link>
        ))}
        {!loading && publikasi.length === 0 && (
          <p className="text-surface-400 col-span-3 text-center py-8">Belum ada hasil yang dipublikasikan.</p>
        )}
      </div>
    </SiswaLayout>
  );
}
