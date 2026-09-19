import { useEffect, useState } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import api from '../../utils/api';
import { User, Mail, ShieldCheck, Briefcase } from 'lucide-react';

export default function AdminProfile() {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    api.get('/auth/me/').then(({ data }) => setProfile(data));
  }, []);

  if (!profile) return <AdminLayout title="Profil Saya"><p className="text-surface-400 text-center py-10">Memuat...</p></AdminLayout>;

  const rows = [
    { icon: User, label: 'Nama', value: profile.nama },
    { icon: Mail, label: 'Email', value: profile.email },
    { icon: ShieldCheck, label: 'Role', value: 'Administrator' },
    { icon: Briefcase, label: 'Jabatan', value: profile.admin?.jabatan },
  ];

  return (
    <AdminLayout title="Profil Saya">
      <div className="card p-6 max-w-md">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-violet-100 flex items-center justify-center text-2xl font-bold text-violet-700">
            {profile.nama?.[0]?.toUpperCase()}
          </div>
          <div>
            <p className="text-lg font-bold text-surface-900">{profile.nama}</p>
            <p className="text-sm text-surface-500">Administrator</p>
          </div>
        </div>
        <div className="space-y-3">
          {rows.map(({ icon: Icon, label, value }) => (
            <div key={label} className="flex items-center gap-3 text-sm">
              <Icon className="w-4 h-4 text-surface-400" />
              <span className="text-surface-500 w-20">{label}</span>
              <span className="font-medium text-surface-800">{value || '-'}</span>
            </div>
          ))}
        </div>
      </div>
    </AdminLayout>
  );
}
