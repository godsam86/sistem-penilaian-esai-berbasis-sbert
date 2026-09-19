import { useEffect, useState } from 'react';
import GuruLayout from '../../components/guru/GuruLayout';
import api from '../../utils/api';
import { SkeletonRows } from '../../components/common/Loading';
import { Plus, X, Trash2, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function GuruSoal() {
  const [list, setList] = useState([]);
  const [kbList, setKbList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm());

  function emptyForm() {
    return { pertanyaan: '', jawaban_acuan: '', knowledge_base_ids: [], concept_units: [{ konsep: '', urutan: 1, bobot: null }] };
  }

  const load = async () => {
    setLoading(true);
    try {
      const [soalRes, kbRes] = await Promise.all([
        api.get('/soal/'),
        api.get('/knowledge-base/'),
      ]);
      setList(soalRes.data.results ?? soalRes.data);
      setKbList((kbRes.data.results ?? kbRes.data).filter(kb => kb.processing_status === 'done'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => { setForm(emptyForm()); setEditing(null); setShowForm(true); setError(''); };
  const openEdit = (soal) => {
    setForm({
      pertanyaan: soal.pertanyaan,
      jawaban_acuan: soal.jawaban_acuan || '',
      knowledge_base_ids: soal.knowledge_base_ids?.length ? soal.knowledge_base_ids : (soal.knowledge_bases || []),
      concept_units: soal.concept_units?.length ? soal.concept_units.map(c => ({ ...c })) : [{ konsep: '', urutan: 1, bobot: null }],
    });
    setEditing(soal.id);
    setShowForm(true);
    setError('');
  };

  const addCU = () => setForm(p => ({ ...p, concept_units: [...p.concept_units, { konsep: '', urutan: p.concept_units.length + 1, bobot: null }] }));
  const removeCU = (idx) => setForm(p => ({ ...p, concept_units: p.concept_units.filter((_, i) => i !== idx) }));
  const updateCU = (idx, konsep) => setForm(p => ({ ...p, concept_units: p.concept_units.map((c, i) => i === idx ? { ...c, konsep } : c) }));

  const toggleKb = (id) => setForm(p => ({
    ...p,
    knowledge_base_ids: p.knowledge_base_ids.includes(id)
      ? p.knowledge_base_ids.filter(x => x !== id)
      : [...p.knowledge_base_ids, id],
  }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    const payload = {
      pertanyaan: form.pertanyaan,
      jawaban_acuan: form.jawaban_acuan,
      knowledge_base_ids: form.knowledge_base_ids,
      concept_units: form.concept_units.filter(c => c.konsep.trim()).map((c, i) => ({ konsep: c.konsep, urutan: i + 1, bobot: c.bobot })),
    };
    try {
      if (editing) await api.put(`/soal/${editing}/`, payload);
      else await api.post('/soal/', payload);
      setShowForm(false);
      load();
    } catch (err) {
      setError(
        typeof err.response?.data === 'object' ? Object.values(err.response.data).flat().join(' ') : 'Gagal menyimpan soal.'
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDeactivate = async (id) => {
    if (!confirm('Nonaktifkan soal ini?')) return;
    await api.delete(`/soal/${id}/`);
    load();
  };

  return (
    <GuruLayout title="Manajemen Soal">
      <div className="flex items-center justify-between mb-5">
        <p className="text-sm text-surface-500">Soal memerlukan minimal 1 Concept Unit dan 1 Knowledge Base yang sudah diproses agar bisa dipakai di ujian.</p>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2 shrink-0">
          <Plus className="w-4 h-4" /> Tambah Soal
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-40 bg-black/40 flex items-center justify-center p-4 overflow-y-auto" onClick={() => setShowForm(false)}>
          <div className="card w-full max-w-2xl p-6 my-8" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-surface-900">{editing ? 'Ubah Soal' : 'Tambah Soal'}</h2>
              <button onClick={() => setShowForm(false)}><X className="w-5 h-5 text-surface-400" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Pertanyaan</label>
                <textarea className="input min-h-[80px]" required value={form.pertanyaan}
                  onChange={e => setForm(p => ({ ...p, pertanyaan: e.target.value }))} />
              </div>
              <div>
                <label className="label">Jawaban Acuan (referensi guru, opsional)</label>
                <textarea className="input min-h-[60px]" value={form.jawaban_acuan}
                  onChange={e => setForm(p => ({ ...p, jawaban_acuan: e.target.value }))} />
              </div>
              <div>
                <label className="label">Knowledge Base rujukan</label>
                {kbList.length === 0 ? (
                  <p className="text-xs text-amber-600">Belum ada Knowledge Base yang selesai diproses.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {kbList.map(kb => (
                      <button type="button" key={kb.id} onClick={() => toggleKb(kb.id)}
                        className={`px-3 py-1.5 rounded-full text-xs font-semibold border ${form.knowledge_base_ids.includes(kb.id) ? 'bg-primary-600 text-white border-primary-600' : 'border-surface-200 text-surface-600'}`}>
                        {kb.judul}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="label !mb-0">Concept Unit</label>
                  <button type="button" onClick={addCU} className="text-primary-600 text-xs font-semibold flex items-center gap-1">
                    <Plus className="w-3.5 h-3.5" /> Tambah CU
                  </button>
                </div>
                <div className="space-y-2">
                  {form.concept_units.map((cu, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <input className="input" placeholder={`Concept Unit #${idx + 1}`} value={cu.konsep}
                        onChange={e => updateCU(idx, e.target.value)} />
                      <button type="button" onClick={() => removeCU(idx)} className="text-red-400 hover:text-red-600">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
              {error && <p className="text-sm text-red-600">{error}</p>}
              <div className="flex justify-end gap-2">
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
            <tr>
              <th className="px-5 py-3">Pertanyaan</th>
              <th className="px-5 py-3">Jumlah CU</th>
              <th className="px-5 py-3">Siap Dipakai</th>
              <th className="px-5 py-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-100">
            {loading ? <SkeletonRows cols={4} /> : list.map(soal => (
              <tr key={soal.id}>
                <td className="px-5 py-3 max-w-md">{soal.pertanyaan}</td>
                <td className="px-5 py-3">{soal.concept_units?.length ?? 0}</td>
                <td className="px-5 py-3">
                  {soal.siap_dipakai ? (
                    <span className="badge bg-green-100 text-green-700 gap-1"><CheckCircle2 className="w-3 h-3" /> Siap</span>
                  ) : (
                    <span className="badge bg-amber-100 text-amber-700 gap-1"><AlertTriangle className="w-3 h-3" /> Belum siap</span>
                  )}
                </td>
                <td className="px-5 py-3 text-right space-x-2">
                  <button onClick={() => openEdit(soal)} className="text-primary-600 hover:underline text-xs">Ubah</button>
                  <button onClick={() => handleDeactivate(soal.id)} className="text-red-500 hover:underline text-xs">Nonaktifkan</button>
                </td>
              </tr>
            ))}
            {!loading && list.length === 0 && (
              <tr><td colSpan={4} className="px-5 py-8 text-center text-surface-400">Belum ada soal.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </GuruLayout>
  );
}
