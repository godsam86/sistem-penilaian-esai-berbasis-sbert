import { useEffect, useState } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import api from '../../utils/api';
import Pagination from '../../components/common/Pagination';
import { SkeletonRows } from '../../components/common/Loading';
import { Search, Download } from 'lucide-react';

/** Admin melihat SELURUH hasil penilaian (bagian 25) -- endpoint sama dengan guru, tanpa filter guru. */
export default function AdminPenilaian() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const load = async (p = page) => {
    setLoading(true);
    try {
      const params = { page: p };
      if (search) params.search = search;
      const { data } = await api.get('/penilaian/hasil/', { params });
      setList(data.results ?? data);
      if (data.count != null) setTotalPages(Math.max(1, Math.ceil(data.count / 20)));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); setPage(1); }, [search]);

  const handleExport = async (format) => {
  const params = {};
  if (search) params.search = search;
  if (ujianFilter) params.ujian_id = ujianFilter;

  try {
    const response = await api.get(`/penilaian/export/${format}/`, {
      params,
      responseType: 'blob',
    });

    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = `hasil_penilaian.${format}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Export gagal:', error);
    alert('Gagal mengexport data.');
  }
};

  return (
    <AdminLayout title="Seluruh Hasil Penilaian">
      <div className="flex flex-wrap items-center gap-3 mb-5">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input className="input pl-9" placeholder="Cari nama / NISN..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <button onClick={() => handleExport('xlsx')} className="btn-secondary flex items-center gap-2"><Download className="w-4 h-4" /> XLSX</button>
        <button onClick={() => handleExport('pdf')} className="btn-secondary flex items-center gap-2"><Download className="w-4 h-4" /> PDF</button>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-surface-50 text-left text-xs font-semibold uppercase text-surface-500">
            <tr><th className="px-5 py-3">Siswa</th><th className="px-5 py-3">Kelas/Jurusan</th><th className="px-5 py-3">Ujian</th><th className="px-5 py-3">Skor</th><th className="px-5 py-3">Status</th></tr>
          </thead>
          <tbody className="divide-y divide-surface-100">
            {loading ? <SkeletonRows cols={5} /> : list.map(p => (
              <tr key={p.id}>
                <td className="px-5 py-3">{p.nama_siswa} <span className="text-surface-400">({p.nisn})</span></td>
                <td className="px-5 py-3">{p.kelas} / {p.jurusan}</td>
                <td className="px-5 py-3">{p.nama_ujian}</td>
                <td className="px-5 py-3 font-bold">{p.final_score != null ? p.final_score.toFixed(2) : '-'}</td>
                <td className="px-5 py-3">
                  <span className={`badge ${p.processing_status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                    {p.processing_status === 'failed' ? 'Gagal' : 'Berhasil'}
                  </span>
                </td>
              </tr>
            ))}
            {!loading && list.length === 0 && <tr><td colSpan={5} className="px-5 py-8 text-center text-surface-400">Belum ada hasil.</td></tr>}
          </tbody>
        </table>
        </div>
        <Pagination page={page} totalPages={totalPages} onPageChange={(p) => { setPage(p); load(p); }} />
      </div>
    </AdminLayout>
  );
}