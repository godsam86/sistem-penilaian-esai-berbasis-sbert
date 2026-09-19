import { useEffect, useState } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import api from '../../utils/api';
import { Plus, X } from 'lucide-react';

function Panel({ title, items, fields, onCreate, onDeactivate }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(Object.fromEntries(fields.map(f => [f.key, ''])));
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await onCreate(form);
      setForm(Object.fromEntries(fields.map(f => [f.key, ''])));
      setShowForm(false);
    } catch (err) {
      setError(typeof err.response?.data === 'object' ? Object.values(err.response.data).flat().join(' ') : 'Gagal menyimpan.');
    }
  };

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-bold text-surface-900">{title}</h2>
        <button onClick={() => setShowForm(p => !p)} className="btn-secondary flex items-center gap-2 text-xs">
          {showForm ? <X className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5" />} {showForm ? 'Tutup' : 'Tambah'}
        </button>
      </div>
      {showForm && (
        <form onSubmit={submit} className="flex flex-wrap items-end gap-2 mb-4 p-3 bg-surface-50 rounded-lg">
          {fields.map(f => (
            <div key={f.key}>
              <label className="label text-xs">{f.label}</label>
              <input className="input" required value={form[f.key]} onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))} />
            </div>
          ))}
          <button type="submit" className="btn-primary text-sm">Simpan</button>
          {error && <p className="text-xs text-red-600 w-full">{error}</p>}
        </form>
      )}
      <ul className="divide-y divide-surface-100">
        {items.map(item => (
          <li key={item.id} className="flex items-center justify-between py-2 text-sm">
            <span>{fields.map(f => item[f.key]).join(' - ')}</span>
            <div className="flex items-center gap-2">
              <span className={`badge ${item.status ? 'bg-green-100 text-green-700' : 'bg-surface-100 text-surface-500'}`}>{item.status ? 'Aktif' : 'Nonaktif'}</span>
              {item.status === 1 && (
                <button onClick={() => onDeactivate(item.id)} className="text-red-500 hover:underline text-xs">Nonaktifkan</button>
              )}
            </div>
          </li>
        ))}
        {items.length === 0 && <li className="py-6 text-center text-surface-400 text-sm">Belum ada data.</li>}
      </ul>
    </div>
  );
}

export default function AdminMasterData() {
  const [kelas, setKelas] = useState([]);
  const [jurusan, setJurusan] = useState([]);

  const loadKelas = () => api.get('/master/kelas/').then(({ data }) => setKelas(data.results ?? data));
  const loadJurusan = () => api.get('/master/jurusan/').then(({ data }) => setJurusan(data.results ?? data));

  useEffect(() => { loadKelas(); loadJurusan(); }, []);

  return (
    <AdminLayout title="Kelas & Jurusan">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Panel
          title="Kelas"
          items={kelas}
          fields={[{ key: 'nama_kelas', label: 'Nama Kelas' }, { key: 'tingkat', label: 'Tingkat' }]}
          onCreate={async (form) => { await api.post('/master/kelas/', form); loadKelas(); }}
          onDeactivate={async (id) => { await api.delete(`/master/kelas/${id}/`); loadKelas(); }}
        />
        <Panel
          title="Jurusan"
          items={jurusan}
          fields={[{ key: 'kode_jurusan', label: 'Kode' }, { key: 'nama_jurusan', label: 'Nama Jurusan' }]}
          onCreate={async (form) => { await api.post('/master/jurusan/', form); loadJurusan(); }}
          onDeactivate={async (id) => { await api.delete(`/master/jurusan/${id}/`); loadJurusan(); }}
        />
      </div>
    </AdminLayout>
  );
}
