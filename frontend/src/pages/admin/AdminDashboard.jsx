import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import AdminLayout from '../../components/admin/AdminLayout';
import api from '../../utils/api';
import { SkeletonCard } from '../../components/common/Loading';
import { Users, GraduationCap, Building2, BarChart3 } from 'lucide-react';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get('/master/guru/'), api.get('/master/siswa/'), api.get('/master/kelas/'),
    ]).then(([guru, siswa, kelas]) => {
      setStats({
        guru: (guru.data.results ?? guru.data).length,
        siswa: (siswa.data.results ?? siswa.data).length,
        kelas: (kelas.data.results ?? kelas.data).length,
      });
    });
  }, []);

  const cards = [
    { to: '/admin/guru', icon: Users, label: 'Akun Guru', value: stats?.guru },
    { to: '/admin/siswa', icon: GraduationCap, label: 'Akun Siswa', value: stats?.siswa },
    { to: '/admin/master-data', icon: Building2, label: 'Kelas', value: stats?.kelas },
    { to: '/admin/penilaian', icon: BarChart3, label: 'Hasil Penilaian', value: '' },
  ];

  return (
    <AdminLayout title="Dashboard Admin">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {!stats ? [...Array(4)].map((_, i) => <SkeletonCard key={i} />) : cards.map(({ to, icon: Icon, label, value }) => (
          <Link to={to} key={label} className="card p-5 hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-violet-50 rounded-xl flex items-center justify-center mb-3">
              <Icon className="w-5 h-5 text-violet-600" />
            </div>
            <p className="text-2xl font-extrabold text-surface-900">{value}</p>
            <p className="text-sm font-semibold text-surface-700 mt-1">{label}</p>
          </Link>
        ))}
      </div>
    </AdminLayout>
  );
}
