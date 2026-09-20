import { useEffect, useState } from 'react';
import { X, Trash2, Pencil, Check, Layers } from 'lucide-react';
import api from '../../utils/api';

/**
 * Kurasi chunk Knowledge Base: lihat, edit isi (re-embed otomatis di backend),
 * dan hapus per chunk -- atas permintaan eksplisit Anda (bagian 9 diperluas).
 */
export default function ChunkCurationModal({ kb, onClose, onChanged }) {
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/knowledge-base/${kb.id}/chunks/`);
      setChunks(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [kb.id]);

  const startEdit = (chunk) => { setEditingId(chunk.id); setEditText(chunk.content); setError(''); };
  const cancelEdit = () => { setEditingId(null); setEditText(''); };

  const saveEdit = async (chunkId) => {
    setSaving(true);
    setError('');
    try {
      const { data } = await api.patch(`/knowledge-base/${kb.id}/chunks/${chunkId}/`, { content: editText });
      setChunks((prev) => prev.map((c) => (c.id === chunkId ? data : c)));
      setEditingId(null);
      onChanged?.();
    } catch (err) {
      setError(
        typeof err.response?.data === 'object'
          ? Object.values(err.response.data).flat().join(' ')
          : 'Gagal menyimpan perubahan chunk.'
      );
    } finally {
      setSaving(false);
    }
  };

  const deleteChunk = async (chunkId) => {
    if (!confirm('Hapus chunk ini? Embedding chunk ini akan hilang dari referensi penilaian.')) return;
    await api.delete(`/knowledge-base/${kb.id}/chunks/${chunkId}/`);
    setChunks((prev) => prev.filter((c) => c.id !== chunkId));
    onChanged?.();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4" onClick={onClose}>
      <div className="card w-full max-w-3xl max-h-[85vh] flex flex-col p-6" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4 shrink-0">
          <h2 className="text-lg font-bold text-surface-900 flex items-center gap-2">
            <Layers className="w-5 h-5 text-primary-600" /> Kurasi Chunk — {kb.judul}
          </h2>
          <button onClick={onClose}><X className="w-5 h-5 text-surface-400" /></button>
        </div>

        {error && <p className="text-sm text-red-600 mb-3">{error}</p>}

        <div className="flex-1 overflow-y-auto space-y-3 pr-1">
          {loading ? (
            <p className="text-surface-400 text-center py-8">Memuat chunk...</p>
          ) : chunks.length === 0 ? (
            <p className="text-surface-400 text-center py-8">Belum ada chunk untuk Knowledge Base ini.</p>
          ) : (
            chunks.map((chunk) => (
              <div key={chunk.id} className="border border-surface-100 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="badge bg-surface-100 text-surface-600">Chunk #{chunk.chunk_index}</span>
                  {editingId === chunk.id ? (
                    <div className="flex items-center gap-2">
                      <button onClick={cancelEdit} className="text-xs text-surface-500 hover:underline">Batal</button>
                      <button onClick={() => saveEdit(chunk.id)} disabled={saving}
                        className="text-xs text-primary-600 font-semibold inline-flex items-center gap-1 hover:underline">
                        <Check className="w-3.5 h-3.5" /> {saving ? 'Menyimpan...' : 'Simpan'}
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center gap-3">
                      <button onClick={() => startEdit(chunk)} className="text-xs text-primary-600 inline-flex items-center gap-1 hover:underline">
                        <Pencil className="w-3.5 h-3.5" /> Edit
                      </button>
                      <button onClick={() => deleteChunk(chunk.id)} className="text-xs text-red-500 inline-flex items-center gap-1 hover:underline">
                        <Trash2 className="w-3.5 h-3.5" /> Hapus
                      </button>
                    </div>
                  )}
                </div>
                {editingId === chunk.id ? (
                  <textarea
                    className="input min-h-[100px] text-sm"
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    autoFocus
                  />
                ) : (
                  <p className="text-sm text-surface-700 whitespace-pre-wrap">{chunk.content}</p>
                )}
              </div>
            ))
          )}
        </div>

        <p className="text-xs text-surface-400 mt-4 shrink-0">
          Mengedit isi chunk otomatis membuat ulang embedding chunk tersebut saja (bukan seluruh Knowledge Base).
          Menghapus chunk tidak memicu proses ulang KB.
        </p>
      </div>
    </div>
  );
}
