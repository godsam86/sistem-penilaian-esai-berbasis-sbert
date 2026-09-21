import { useEffect, useState } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import api from '../../utils/api';
import { SkeletonRows } from '../../components/common/Loading';
import Pagination from '../../components/common/Pagination';
import { Plus, X, Search } from 'lucide-react';

export default function AdminGuru() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ nama: '', email: '', password: '', nip: '' });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const load = async (targetPage = page) => {
    setLoading(true);
    try {
      const params = { page: targetPage };
      if (search) params.search = search;
      const { data } = await api.get('/master/guru/', { params });
      setList(data.results ?? data);
      if (data.count != null) setTotalPages(Math.max(1, Math.ceil(data.count / 10)));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { setPage(1); load(1); }, [search]);

  const openCreate = () => { setForm({ nama: '', email: '', password: '', nip: '' }); setEditing(null); setShowForm(true); setError(''); };
  const openEdit = (g) => { setForm({ nama: g.nama, email: g.email, password: '', nip: g.nip || '' }); setEditing(g.id); setShowForm(true); setError(''); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      if (editing) await api.put(`/master/guru/${editing}/`, form);
      else await api.post('/master/guru/', form);
      setShowForm(false);
      load();
    } catch (err) {
      setError(typeof err.response?.data === 'object' ? Object.values(err.response.data).flat().join(' ') : 'Gagal menyimpan.');
    } finally {
      setSaving(false);
    }
  };

  const handleDeactivate = async (id) => {
    if (!confirm('Nonaktifkan akun guru ini?')) return;
    await api.delete(`/master/guru/${id}/`);
    load();
  };
  const handleActivate = async (id) => {
    if (!confirm('Aktifkan kembali akun guru ini?')) return;
    await api.post(`/master/guru/${id}/aktifkan/`);
    load();
  };

  return (
    <AdminLayout title="Akun Guru">
      <div className="flex flex-wrap items-center gap-3 mb-5">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input className="input pl-9" placeholder="Cari nama / email..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2"><Plus className="w-4 h-4" /> Tambah Guru</button>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-40 bg-black/40 flex items-center justify-center p-4" onClick={() => setShowForm(false)}>
          <div className="card w-full max-w-md p-6" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-surface-900">{editing ? 'Ubah Guru' : 'Tambah Guru'}</h2>
              <button onClick={() => setShowForm(false)}><X className="w-5 h-5 text-surface-400" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div><label className="label">Nama</label><input className="input" required value={form.nama} onChange={e => setForm(p => ({ ...p, nama: e.target.value }))} /></div>
              <div><label className="label">Email</label><input type="email" className="input" required value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} /></div>
              <div><label className="label">NIP (opsional)</label><input className="input" value={form.nip} onChange={e => setForm(p => ({ ...p, nip: e.target.value }))} /></div>
              <div><label className="label">{editing ? 'Password baru (opsional)' : 'Password'}</label><input type="password" className="input" required={!editing} value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))} /></div>
              {error && <p className="text-sm text-red-600">{error}</p>}
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Batal</button>
                <button type="submit" disabled={saving} className="btn-primary">{saving ? 'Menyimpan...' : 'Simpan'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-surface-50 text-left text-xs font-semibold uppercase text-surface-500">
            <tr><th className="px-5 py-3">Nama</th><th className="px-5 py-3">Email</th><th className="px-5 py-3">NIP</th><th className="px-5 py-3">Status</th><th className="px-5 py-3 text-right">Aksi</th></tr>
          </thead>
          <tbody className="divide-y divide-surface-100">
            {loading ? <SkeletonRows cols={5} /> : list.map(g => (
              <tr key={g.id}>
                <td className="px-5 py-3 font-medium text-surface-800">{g.nama}</td>
                <td className="px-5 py-3">{g.email}</td>
                <td className="px-5 py-3">{g.nip || '-'}</td>
                <td className="px-5 py-3"><span className={`badge ${g.status ? 'bg-green-100 text-green-700' : 'bg-surface-100 text-surface-500'}`}>{g.status ? 'Aktif' : 'Nonaktif'}</span></td>
                <td className="px-5 py-3 text-right space-x-2">
                  <button onClick={() => openEdit(g)} className="text-primary-600 hover:underline text-xs">Ubah</button>
                  {g.status ? (
                    <button onClick={() => handleDeactivate(g.id)} className="text-red-500 hover:underline text-xs">Nonaktifkan</button>
                  ) : (
                    <button onClick={() => handleActivate(g.id)} className="text-green-600 hover:underline text-xs">Aktifkan</button>
                  )}
                </td>
              </tr>
            ))}
            {!loading && list.length === 0 && <tr><td colSpan={5} className="px-5 py-8 text-center text-surface-400">Belum ada akun guru.</td></tr>}
          </tbody>
        </table>
        <Pagination page={page} totalPages={totalPages} onPageChange={(p) => { setPage(p); load(p); }} />
      </div>
    </AdminLayout>
  );
}