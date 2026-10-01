import { useEffect, useState } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import api from '../../utils/api';
import { SkeletonRows } from '../../components/common/Loading';
import Pagination from '../../components/common/Pagination';
import { Plus, X, Search, Upload, Download, CheckCircle2, XCircle } from 'lucide-react';

export default function AdminSiswa() {
  const [list, setList] = useState([]);
  const [kelasOptions, setKelasOptions] = useState([]);
  const [jurusanOptions, setJurusanOptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [kelasFilter, setKelasFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm());
  const [showImport, setShowImport] = useState(false);
  const [importKelas, setImportKelas] = useState('');
  const [importJurusan, setImportJurusan] = useState('');
  const [importFile, setImportFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [importError, setImportError] = useState('');

  function emptyForm() { return { nama: '', email: '', nisn: '', kelas: '', jurusan: '' }; }

  const load = async (targetPage = page) => {
    setLoading(true);
    try {
      const params = { page: targetPage };
      if (search) params.search = search;
      if (kelasFilter) params.kelas_id = kelasFilter;
      const { data } = await api.get('/master/siswa/', { params });
      setList(data.results ?? data);
      if (data.count != null) setTotalPages(Math.max(1, Math.ceil(data.count / 10)));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    api.get('/master/kelas/').then(({ data }) => setKelasOptions(data.results ?? data));
    api.get('/master/jurusan/').then(({ data }) => setJurusanOptions(data.results ?? data));
  }, []);

  useEffect(() => { setPage(1); load(1); }, [search, kelasFilter]);

  const openCreate = () => { setForm(emptyForm()); setEditing(null); setShowForm(true); setError(''); };
  const openEdit = (s) => {
    setForm({ nama: s.nama, email: s.email, nisn: s.nisn, kelas: s.kelas, jurusan: s.jurusan });
    setEditing(s.id); setShowForm(true); setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      if (editing) await api.put(`/master/siswa/${editing}/`, form);
      else await api.post('/master/siswa/', form);
      setShowForm(false);
      load();
    } catch (err) {
      setError(typeof err.response?.data === 'object' ? Object.values(err.response.data).flat().join(' ') : 'Gagal menyimpan.');
    } finally {
      setSaving(false);
    }
  };

  const handleDeactivate = async (id) => {
    if (!confirm('Nonaktifkan akun siswa ini?')) return;
    await api.delete(`/master/siswa/${id}/`);
    load();
  };
  const handleActivate = async (id) => {
    if (!confirm('Aktifkan kembali akun siswa ini?')) return;
    await api.post(`/master/siswa/${id}/aktifkan/`);
    load();
  };

  const openImport = () => {
    setImportKelas(''); setImportJurusan(''); setImportFile(null);
    setImportResult(null); setImportError(''); setShowImport(true);
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await api.get('/master/siswa/template/', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'template-impor-siswa.xlsx';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Unduh template gagal:', error);
      alert('Gagal mengunduh template.');
    }
  };

  const handleImportSubmit = async (e) => {
    e.preventDefault();
    setImporting(true);
    setImportError('');
    setImportResult(null);
    try {
      const payload = new FormData();
      payload.append('file', importFile);
      payload.append('kelas', importKelas);
      payload.append('jurusan', importJurusan);
      const { data } = await api.post('/master/siswa/impor/', payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setImportResult(data);
      load();
    } catch (err) {
      setImportError(
        typeof err.response?.data === 'object'
          ? Object.values(err.response.data).flat().join(' ')
          : 'Gagal mengimpor file.'
      );
    } finally {
      setImporting(false);
    }
  };

  return (
    <AdminLayout title="Akun Siswa">
      <div className="flex flex-wrap items-center gap-3 mb-5">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input className="input pl-9" placeholder="Cari nama / NISN..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="input w-48" value={kelasFilter} onChange={e => setKelasFilter(e.target.value)}>
          <option value="">Semua Kelas</option>
          {kelasOptions.map(k => <option key={k.id} value={k.id}>{k.nama_kelas}</option>)}
        </select>
        <button onClick={openImport} className="btn-secondary flex items-center gap-2"><Upload className="w-4 h-4" /> Impor Excel</button>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2"><Plus className="w-4 h-4" /> Tambah Siswa</button>
      </div>

      {showImport && (
        <div className="fixed inset-0 z-40 bg-black/40 flex items-center justify-center p-4" onClick={() => setShowImport(false)}>
          <div className="card w-full max-w-lg p-6 max-h-[85vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-surface-900">Impor Siswa dari Excel</h2>
              <button onClick={() => setShowImport(false)}><X className="w-5 h-5 text-surface-400" /></button>
            </div>

            <button onClick={handleDownloadTemplate} className="btn-secondary w-full flex items-center justify-center gap-2 mb-4">
              <Download className="w-4 h-4" /> Unduh Template Excel
            </button>
            <p className="text-xs text-surface-400 mb-4">
              Format kolom: <b>Nama</b>, <b>Email</b>, <b>NISN</b> (baris pertama judul kolom, jangan diubah/dihapus).
              Semua siswa dalam file akan dimasukkan ke SATU kelas &amp; jurusan yang Anda pilih di bawah.
            </p>

            <form onSubmit={handleImportSubmit} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label">Kelas Tujuan</label>
                  <select className="input" required value={importKelas} onChange={e => setImportKelas(e.target.value)}>
                    <option value="">Pilih</option>
                    {kelasOptions.map(k => <option key={k.id} value={k.id}>{k.nama_kelas}</option>)}
                  </select>
                </div>
                <div>
                  <label className="label">Jurusan Tujuan</label>
                  <select className="input" required value={importJurusan} onChange={e => setImportJurusan(e.target.value)}>
                    <option value="">Pilih</option>
                    {jurusanOptions.map(j => <option key={j.id} value={j.id}>{j.kode_jurusan}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="label">File Excel (.xlsx)</label>
                <input type="file" accept=".xlsx" required className="input"
                  onChange={e => setImportFile(e.target.files[0])} />
              </div>

              {importError && <p className="text-sm text-red-600">{importError}</p>}

              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowImport(false)} className="btn-secondary">Tutup</button>
                <button type="submit" disabled={importing} className="btn-primary">
                  {importing ? 'Mengimpor...' : 'Impor Sekarang'}
                </button>
              </div>
            </form>

            {importResult && (
              <div className="mt-5 border-t border-surface-100 pt-4 space-y-3">
                <p className="text-sm font-semibold text-green-700 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> {importResult.berhasil.length} siswa berhasil ditambahkan
                </p>
                {importResult.gagal.length > 0 && (
                  <div>
                    <p className="text-sm font-semibold text-red-600 flex items-center gap-1 mb-1">
                      <XCircle className="w-4 h-4" /> {importResult.gagal.length} baris gagal
                    </p>
                    <ul className="text-xs text-red-500 space-y-1 max-h-32 overflow-y-auto">
                      {importResult.gagal.map((g, i) => (
                        <li key={i}>Baris {g.baris}: {g.alasan}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 z-40 bg-black/40 flex items-center justify-center p-4" onClick={() => setShowForm(false)}>
          <div className="card w-full max-w-md p-6" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-surface-900">{editing ? 'Ubah Siswa' : 'Tambah Siswa'}</h2>
              <button onClick={() => setShowForm(false)}><X className="w-5 h-5 text-surface-400" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div><label className="label">Nama</label><input className="input" required value={form.nama} onChange={e => setForm(p => ({ ...p, nama: e.target.value }))} /></div>
              <div><label className="label">Email</label><input type="email" className="input" required value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} /></div>
              <div><label className="label">NISN</label><input className="input" required value={form.nisn} onChange={e => setForm(p => ({ ...p, nisn: e.target.value }))} /></div>
              <div className="grid grid-cols-2 gap-3">
                <div><label className="label">Kelas</label>
                  <select className="input" required value={form.kelas} onChange={e => setForm(p => ({ ...p, kelas: e.target.value }))}>
                    <option value="">Pilih</option>
                    {kelasOptions.map(k => <option key={k.id} value={k.id}>{k.nama_kelas}</option>)}
                  </select>
                </div>
                <div><label className="label">Jurusan</label>
                  <select className="input" required value={form.jurusan} onChange={e => setForm(p => ({ ...p, jurusan: e.target.value }))}>
                    <option value="">Pilih</option>
                    {jurusanOptions.map(j => <option key={j.id} value={j.id}>{j.kode_jurusan}</option>)}
                  </select>
                </div>
              </div>
              <p className="text-xs text-surface-400">Siswa login menggunakan NISN sebagai kredensial, bukan password.</p>
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
        <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-surface-50 text-left text-xs font-semibold uppercase text-surface-500">
            <tr><th className="px-5 py-3">Nama</th><th className="px-5 py-3">NISN</th><th className="px-5 py-3">Kelas</th><th className="px-5 py-3">Jurusan</th><th className="px-5 py-3">Status</th><th className="px-5 py-3 text-right">Aksi</th></tr>
          </thead>
          <tbody className="divide-y divide-surface-100">
            {loading ? <SkeletonRows cols={6} /> : list.map(s => (
              <tr key={s.id}>
                <td className="px-5 py-3 font-medium text-surface-800">{s.nama}</td>
                <td className="px-5 py-3">{s.nisn}</td>
                <td className="px-5 py-3">{kelasOptions.find(k => k.id === s.kelas)?.nama_kelas ?? s.kelas}</td>
                <td className="px-5 py-3">{jurusanOptions.find(j => j.id === s.jurusan)?.kode_jurusan ?? s.jurusan}</td>
                <td className="px-5 py-3"><span className={`badge ${s.status ? 'bg-green-100 text-green-700' : 'bg-surface-100 text-surface-500'}`}>{s.status ? 'Aktif' : 'Nonaktif'}</span></td>
                <td className="px-5 py-3 text-right space-x-2">
                  <button onClick={() => openEdit(s)} className="text-primary-600 hover:underline text-xs">Ubah</button>
                  {s.status ? (
                    <button onClick={() => handleDeactivate(s.id)} className="text-red-500 hover:underline text-xs">Nonaktifkan</button>
                  ) : (
                    <button onClick={() => handleActivate(s.id)} className="text-green-600 hover:underline text-xs">Aktifkan</button>
                  )}
                </td>
              </tr>
            ))}
            {!loading && list.length === 0 && <tr><td colSpan={6} className="px-5 py-8 text-center text-surface-400">Belum ada akun siswa.</td></tr>}
          </tbody>
        </table>
        </div>
        <Pagination page={page} totalPages={totalPages} onPageChange={(p) => { setPage(p); load(p); }} />
      </div>
    </AdminLayout>
  );
}