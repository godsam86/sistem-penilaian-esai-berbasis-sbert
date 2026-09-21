import { useEffect, useState } from 'react';
import GuruLayout from '../../components/guru/GuruLayout';
import api from '../../utils/api';
import { SkeletonRows } from '../../components/common/Loading';
import { Plus, X, Copy, Eye, EyeOff } from 'lucide-react';

export default function GuruUjian() {
  const [list, setList] = useState([]);
  const [soalOptions, setSoalOptions] = useState([]);
  const [kelasOptions, setKelasOptions] = useState([]);
  const [jurusanOptions, setJurusanOptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm());

  function emptyForm() {
    return { nama_ujian: '', jenis_ujian: 'UTS', kelas_id: '', jurusan_id: '', soal_ids: [] };
  }

  const load = async () => {
    setLoading(true);
    try {
      const [ujianRes, soalRes] = await Promise.all([api.get('/ujian/'), api.get('/soal/', { params: { page_size: 1000 } })]);
      setList(ujianRes.data.results ?? ujianRes.data);
      setSoalOptions((soalRes.data.results ?? soalRes.data).filter(s => s.siap_dipakai));
    } finally {
      setLoading(false);
    }
  };

  const loadMasterData = async () => {
    try {
      const [kelasRes, jurusanRes] = await Promise.all([
        api.get('/master/kelas/'), api.get('/master/jurusan/'),
      ]);
      setKelasOptions(kelasRes.data.results ?? kelasRes.data);
      setJurusanOptions(jurusanRes.data.results ?? jurusanRes.data);
    } catch {
      // Guru tidak punya izin akses /master/kelas & /master/jurusan langsung (khusus admin) --
      // fallback: opsi kelas/jurusan bisa didapat dari daftar ujian/siswa yang sudah ada.
    }
  };

  useEffect(() => { load(); loadMasterData(); }, []);

  const toggleSoal = (id) => setForm(p => ({
    ...p, soal_ids: p.soal_ids.includes(id) ? p.soal_ids.filter(x => x !== id) : [...p.soal_ids, id],
  }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.post('/ujian/', {
        nama_ujian: form.nama_ujian,
        jenis_ujian: form.jenis_ujian,
        kelas_id: form.kelas_id,
        jurusan_id: form.jurusan_id,
        soal_items: form.soal_ids.map((id, i) => ({ soal_id: id, urutan: i + 1 })),
      });
      setShowForm(false);
      setForm(emptyForm());
      load();
    } catch (err) {
      setError(
        typeof err.response?.data === 'object' ? Object.values(err.response.data).flat().join(' ') : 'Gagal membuat ujian.'
      );
    } finally {
      setSaving(false);
    }
  };

  const togglePublikasi = async (ujian) => {
    await api.post(`/ujian/${ujian.id}/publikasikan/`, { hasil_published: !ujian.hasil_published });
    load();
  };

  return (
    <GuruLayout title="Manajemen Ujian">
      <div className="flex items-center justify-between mb-5">
        <p className="text-sm text-surface-500">Token 5 huruf kapital dibuat otomatis & unik untuk ujian aktif.</p>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Buat Ujian
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-40 bg-black/40 flex items-center justify-center p-4 overflow-y-auto" onClick={() => setShowForm(false)}>
          <div className="card w-full max-w-xl p-6 my-8" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-surface-900">Buat Ujian</h2>
              <button onClick={() => setShowForm(false)}><X className="w-5 h-5 text-surface-400" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Nama Ujian</label>
                <input className="input" required placeholder="UTS Bahasa Indonesia" value={form.nama_ujian}
                  onChange={e => setForm(p => ({ ...p, nama_ujian: e.target.value }))} />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="label">Jenis</label>
                  <select className="input" value={form.jenis_ujian} onChange={e => setForm(p => ({ ...p, jenis_ujian: e.target.value }))}>
                    {['UTS', 'UAS', 'Ulangan Harian', 'Ujian Semester'].map(j => <option key={j}>{j}</option>)}
                  </select>
                </div>
                <div>
                  <label className="label">Kelas</label>
                  <select className="input" required value={form.kelas_id} onChange={e => setForm(p => ({ ...p, kelas_id: e.target.value }))}>
                    <option value="">Pilih</option>
                    {kelasOptions.map(k => <option key={k.id} value={k.id}>{k.nama_kelas}</option>)}
                  </select>
                </div>
                <div>
                  <label className="label">Jurusan</label>
                  <select className="input" required value={form.jurusan_id} onChange={e => setForm(p => ({ ...p, jurusan_id: e.target.value }))}>
                    <option value="">Pilih</option>
                    {jurusanOptions.map(j => <option key={j.id} value={j.id}>{j.kode_jurusan}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="label">Pilih Soal</label>
                {soalOptions.length === 0 ? (
                  <p className="text-xs text-amber-600">Belum ada soal yang siap dipakai (butuh CU + KB).</p>
                ) : (
                  <div className="space-y-1.5 max-h-52 overflow-y-auto border border-surface-100 rounded-lg p-2">
                    {soalOptions.map(s => (
                      <label key={s.id} className="flex items-center gap-2 text-sm px-2 py-1.5 rounded hover:bg-surface-50">
                        <input type="checkbox" checked={form.soal_ids.includes(s.id)} onChange={() => toggleSoal(s.id)} />
                        {s.pertanyaan}
                      </label>
                    ))}
                  </div>
                )}
              </div>
              {error && <p className="text-sm text-red-600">{error}</p>}
              <div className="flex justify-end gap-2">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Batal</button>
                <button type="submit" disabled={saving || form.soal_ids.length === 0} className="btn-primary">
                  {saving ? 'Menyimpan...' : 'Buat Ujian'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-surface-50 text-left text-xs font-semibold uppercase text-surface-500">
            <tr>
              <th className="px-5 py-3">Nama Ujian</th>
              <th className="px-5 py-3">Jenis</th>
              <th className="px-5 py-3">Jumlah Soal</th>
              <th className="px-5 py-3">Token</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-100">
            {loading ? <SkeletonRows cols={6} /> : list.map(u => (
              <tr key={u.id}>
                <td className="px-5 py-3 font-medium text-surface-800">{u.nama_ujian}</td>
                <td className="px-5 py-3">{u.jenis_ujian}</td>
                <td className="px-5 py-3">{u.jumlah_soal}</td>
                <td className="px-5 py-3">
                  <button onClick={() => { navigator.clipboard.writeText(u.token); }}
                    className="font-mono font-bold text-primary-700 flex items-center gap-1">
                    {u.token} <Copy className="w-3 h-3" />
                  </button>
                </td>
                <td className="px-5 py-3"><span className="badge bg-surface-100 text-surface-600">{u.status}</span></td>
                <td className="px-5 py-3 text-right">
                  <button onClick={() => togglePublikasi(u)} className="text-primary-600 hover:underline text-xs inline-flex items-center gap-1">
                    {u.hasil_published ? <><EyeOff className="w-3 h-3" /> Batalkan publikasi</> : <><Eye className="w-3 h-3" /> Publikasikan hasil</>}
                  </button>
                </td>
              </tr>
            ))}
            {!loading && list.length === 0 && (
              <tr><td colSpan={6} className="px-5 py-8 text-center text-surface-400">Belum ada ujian.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </GuruLayout>
  );
}