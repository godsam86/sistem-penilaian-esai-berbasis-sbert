import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SiswaLayout from '../../components/siswa/SiswaLayout';
import api from '../../utils/api';
import { SkeletonCard } from '../../components/common/Loading';
import { ClipboardList, History, BarChart2 } from 'lucide-react';

export default function SiswaDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    Promise.all([api.get('/ujian/tersedia/'), api.get('/jawaban/riwayat/')]).then(([ujian, riwayat]) => {
      setStats({
        tersedia: ujian.data.filter(u => !u.sudah_dikerjakan).length,
        riwayat: new Set(riwayat.data.map(j => j.ujian)).size,
      });
    });
  }, []);

  const cards = [
    { to: '/siswa/ujian', icon: ClipboardList, label: 'Ujian Tersedia', value: stats?.tersedia },
    { to: '/siswa/riwayat', icon: History, label: 'Riwayat Ujian', value: stats?.riwayat },
    { to: '/siswa/hasil', icon: BarChart2, label: 'Hasil Ujian', value: '' },
  ];

  return (
    <SiswaLayout title="Beranda">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {!stats ? [...Array(3)].map((_, i) => <SkeletonCard key={i} />) : cards.map(({ to, icon: Icon, label, value }) => (
          <Link to={to} key={label} className="card p-5 hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center mb-3">
              <Icon className="w-5 h-5 text-primary-600" />
            </div>
            <p className="text-2xl font-extrabold text-surface-900">{value}</p>
            <p className="text-sm font-semibold text-surface-700 mt-1">{label}</p>
          </Link>
        ))}
      </div>
    </SiswaLayout>
  );
}
