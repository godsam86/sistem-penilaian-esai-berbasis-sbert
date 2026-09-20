import { useEffect, useState } from 'react';
import GuruLayout from '../../components/guru/GuruLayout';
import api from '../../utils/api';
import { SkeletonRows } from '../../components/common/Loading';
import ChunkCurationModal from '../../components/guru/ChunkCurationModal';
import { Plus, RefreshCw, X, FileText, Type, Upload, Layers } from 'lucide-react';

const STATUS_LABEL = {
  pending: 'Menunggu', processing: 'Diproses', done: 'Selesai',
  failed: 'Gagal', needs_ocr: 'Butuh OCR',
};
const STATUS_BADGE = {
  pending: 'bg-surface-100 text-surface-600', processing: 'bg-blue-100 text-blue-700',
  done: 'bg-green-100 text-green-700', failed: 'bg-red-100 text-red-700',
  needs_ocr: 'bg-amber-100 text-amber-700',
};

export default function GuruKB() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ judul: '', sumber: 'text', teks: '', file: null });
  const [curatingKb, setCuratingKb] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/knowledge-base/');
      setList(data.results ?? data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const resetForm = () => {
    setForm({ judul: '', sumber: 'text', teks: '', file: null });
    setError('');
    setShowForm(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = new FormData();
      payload.append('judul', form.judul);
      payload.append('sumber', form.sumber);
      if (form.sumber === 'text') payload.append('teks', form.teks);
      if (form.file) payload.append('file', form.file);

      await api.post('/knowledge-base/', payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      resetForm();
      load();
    } catch (err) {
      setError(
        typeof err.response?.data === 'object'
          ? Object.values(err.response.data).flat().join(' ')
          : 'Gagal menyimpan Knowledge Base.'
      );
    } finally {
      setSaving(false);
    }
  };

  const handleReprocess = async (id) => {
    await api.post(`/knowledge-base/${id}/reprocess/`);
    load();
  };

  const handleDeactivate = async (id) => {
    if (!confirm('Nonaktifkan Knowledge Base ini?')) return;
    await api.delete(`/knowledge-base/${id}/`);
    load();
  };

  return (
    <GuruLayout title="Knowledge Base">
      <div className="flex items-center justify-between mb-5">
        <p className="text-sm text-surface-500">Materi rujukan untuk penilaian semantik soal Anda.</p>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Tambah Knowledge Base
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-40 bg-black/40 flex items-center justify-center p-4" onClick={resetForm}>
          <div className="card w-full max-w-lg p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-surface-900">Tambah Knowledge Base</h2>
              <button onClick={resetForm}><X className="w-5 h-5 text-surface-400" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Judul</label>
                <input className="input" required value={form.judul}
                  onChange={e => setForm(p => ({ ...p, judul: e.target.value }))} />
              </div>
              <div>
                <label className="label">Sumber</label>
                <div className="flex gap-2">
                  {[['text', 'Teks langsung', Type], ['pdf', 'PDF', FileText], ['docx', 'DOCX', Upload]].map(([val, label, Icon]) => (
                    <button type="button" key={val}
                      onClick={() => setForm(p => ({ ...p, sumber: val }))}
                      className={`flex-1 flex flex-col items-center gap-1 rounded-lg border px-3 py-2.5 text-xs font-semibold ${form.sumber === val ? 'border-primary-600 bg-primary-50 text-primary-700' : 'border-surface-200 text-surface-500'}`}>
                      <Icon className="w-4 h-4" /> {label}
                    </button>
                  ))}
                </div>
              </div>
              {form.sumber === 'text' ? (
                <div>
                  <label className="label">Teks materi</label>
                  <textarea className="input min-h-[140px]" required value={form.teks}
                    onChange={e => setForm(p => ({ ...p, teks: e.target.value }))} />
                </div>
              ) : (
                <div>
                  <label className="label">File ({form.sumber.toUpperCase()})</label>
                  <input type="file" accept={form.sumber === 'pdf' ? '.pdf' : '.docx'} required
                    className="input" onChange={e => setForm(p => ({ ...p, file: e.target.files[0] }))} />
                </div>
              )}
              {error && <p className="text-sm text-red-600">{error}</p>}
              <div className="flex justify-end gap-2">
                <button type="button" onClick={resetForm} className="btn-secondary">Batal</button>
                <button type="submit" disabled={saving} className="btn-primary">
                  {saving ? 'Memproses...' : 'Simpan & Proses'}
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
              <th className="px-5 py-3">Judul</th>
              <th className="px-5 py-3">Sumber</th>
              <th className="px-5 py-3">Jumlah Chunk</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-100">
            {loading ? <SkeletonRows cols={5} /> : list.map(kb => (
              <tr key={kb.id}>
                <td className="px-5 py-3 font-medium text-surface-800">{kb.judul}</td>
                <td className="px-5 py-3 uppercase text-surface-500 text-xs">{kb.sumber}</td>
                <td className="px-5 py-3">{kb.jumlah_chunk}</td>
                <td className="px-5 py-3">
                  <span className={`badge ${STATUS_BADGE[kb.processing_status]}`}>{STATUS_LABEL[kb.processing_status]}</span>
                  {kb.processing_error && <p className="text-xs text-red-500 mt-1">{kb.processing_error}</p>}
                </td>
                <td className="px-5 py-3 text-right space-x-2">
                  <button onClick={() => setCuratingKb(kb)} className="text-primary-600 hover:underline text-xs inline-flex items-center gap-1">
                    <Layers className="w-3 h-3" /> Lihat Chunk
                  </button>
                  {kb.processing_status === 'failed' && (
                    <button onClick={() => handleReprocess(kb.id)} className="text-primary-600 hover:underline text-xs inline-flex items-center gap-1">
                      <RefreshCw className="w-3 h-3" /> Coba lagi
                    </button>
                  )}
                  <button onClick={() => handleDeactivate(kb.id)} className="text-red-500 hover:underline text-xs">Nonaktifkan</button>
                </td>
              </tr>
            ))}
            {!loading && list.length === 0 && (
              <tr><td colSpan={5} className="px-5 py-8 text-center text-surface-400">Belum ada Knowledge Base.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {curatingKb && (
        <ChunkCurationModal
          kb={curatingKb}
          onClose={() => setCuratingKb(null)}
          onChanged={load}
        />
      )}
    </GuruLayout>
  );
}
