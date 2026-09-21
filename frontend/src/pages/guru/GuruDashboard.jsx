import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import GuruLayout from '../../components/guru/GuruLayout';
import api from '../../utils/api';
import { SkeletonCard } from '../../components/common/Loading';
import { Database, FileText, ClipboardList, BarChart3 } from 'lucide-react';

export default function GuruDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    // page_size=1000: dashboard butuh hitung dari SELURUH data guru ini
    // (termasuk untuk sub-angka "siap dipakai"/"aktif"), bukan cuma 10
    // baris pertama yang dikembalikan pagination default.
    Promise.all([
      api.get('/knowledge-base/', { params: { page_size: 1000 } }),
      api.get('/soal/', { params: { page_size: 1000 } }),
      api.get('/ujian/', { params: { page_size: 1000 } }),
    ]).then(([kb, soal, ujian]) => {
      const kbList = kb.data.results ?? kb.data;
      const soalList = soal.data.results ?? soal.data;
      const ujianList = ujian.data.results ?? ujian.data;
      setStats({
        kb: kb.data.count ?? kbList.length,
        soal: soal.data.count ?? soalList.length,
        soalSiap: soalList.filter(s => s.siap_dipakai).length,
        ujian: ujian.data.count ?? ujianList.length,
        ujianAktif: ujianList.filter(u => u.status === 'aktif').length,
      });
    });
  }, []);

  const cards = [
    { to: '/guru/kb', icon: Database, label: 'Knowledge Base', value: stats?.kb, sub: 'materi rujukan' },
    { to: '/guru/soal', icon: FileText, label: 'Soal', value: stats?.soal, sub: `${stats?.soalSiap ?? 0} siap dipakai` },
    { to: '/guru/ujian', icon: ClipboardList, label: 'Ujian', value: stats?.ujian, sub: `${stats?.ujianAktif ?? 0} aktif` },
    { to: '/guru/hasil', icon: BarChart3, label: 'Hasil Penilaian', value: '', sub: 'lihat detail' },
  ];

  return (
    <GuruLayout title="Dashboard Guru">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {!stats ? [...Array(4)].map((_, i) => <SkeletonCard key={i} />) : cards.map(({ to, icon: Icon, label, value, sub }) => (
          <Link to={to} key={label} className="card p-5 hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center mb-3">
              <Icon className="w-5 h-5 text-primary-600" />
            </div>
            <p className="text-2xl font-extrabold text-surface-900">{value}</p>
            <p className="text-sm font-semibold text-surface-700 mt-1">{label}</p>
            <p className="text-xs text-surface-400">{sub}</p>
          </Link>
        ))}
      </div>
    </GuruLayout>
  );
}