import { useEffect, useState } from 'react';
import GuruLayout from '../../components/guru/GuruLayout';
import api from '../../utils/api';
import Pagination from '../../components/common/Pagination';
import { SkeletonRows } from '../../components/common/Loading';
import { Search, Download, X, RefreshCw } from 'lucide-react';

export default function GuruHasil() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [ujianOptions, setUjianOptions] = useState([]);
  const [ujianFilter, setUjianFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [detail, setDetail] = useState(null);

  const load = async (p = page) => {
    setLoading(true);
    try {
      const params = { page: p };
      if (search) params.search = search;
      if (ujianFilter) params.ujian_id = ujianFilter;
      const { data } = await api.get('/penilaian/hasil/', { params });
      setList(data.results ?? data);
      if (data.count != null) setTotalPages(Math.max(1, Math.ceil(data.count / 20)));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    api.get('/ujian/').then(({ data }) => setUjianOptions(data.results ?? data));
  }, []);

  useEffect(() => { load(1); setPage(1); }, [search, ujianFilter]);

  const handleExport = (format) => {
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (ujianFilter) params.set('ujian_id', ujianFilter);
    window.open(`/api/penilaian/export/${format}/?${params.toString()}`, '_blank');
  };

  const handleRetry = async (id) => {
    await api.post(`/penilaian/hasil/${id}/retry/`);
    load(page);
  };

  return (
    <GuruLayout title="Hasil Penilaian">
      <div className="flex flex-wrap items-center gap-3 mb-5">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input className="input pl-9" placeholder="Cari nama / NISN..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="input w-56" value={ujianFilter} onChange={e => setUjianFilter(e.target.value)}>
          <option value="">Semua Ujian</option>
          {ujianOptions.map(u => <option key={u.id} value={u.id}>{u.nama_ujian}</option>)}
        </select>
        <button onClick={() => handleExport('xlsx')} className="btn-secondary flex items-center gap-2">
          <Download className="w-4 h-4" /> XLSX
        </button>
        <button onClick={() => handleExport('pdf')} className="btn-secondary flex items-center gap-2">
          <Download className="w-4 h-4" /> PDF
        </button>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-surface-50 text-left text-xs font-semibold uppercase text-surface-500">
            <tr>
              <th className="px-5 py-3">Siswa</th>
              <th className="px-5 py-3">NISN</th>
              <th className="px-5 py-3">Ujian</th>
              <th className="px-5 py-3">Skor Akhir</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-100">
            {loading ? <SkeletonRows cols={6} /> : list.map(p => (
              <tr key={p.id}>
                <td className="px-5 py-3">{p.nama_siswa}</td>
                <td className="px-5 py-3">{p.nisn}</td>
                <td className="px-5 py-3">{p.nama_ujian}</td>
                <td className="px-5 py-3 font-bold">{p.final_score != null ? p.final_score.toFixed(2) : '-'}</td>
                <td className="px-5 py-3">
                  <span className={`badge ${p.processing_status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                    {p.processing_status === 'failed' ? 'Gagal Diproses' : 'Berhasil'}
                  </span>
                </td>
                <td className="px-5 py-3 text-right space-x-2">
                  {p.processing_status === 'failed' && (
                    <button onClick={() => handleRetry(p.id)} className="text-primary-600 hover:underline text-xs inline-flex items-center gap-1">
                      <RefreshCw className="w-3 h-3" /> Retry
                    </button>
                  )}
                  <button onClick={() => setDetail(p)} className="text-primary-600 hover:underline text-xs">Detail</button>
                </td>
              </tr>
            ))}
            {!loading && list.length === 0 && (
              <tr><td colSpan={6} className="px-5 py-8 text-center text-surface-400">Belum ada hasil.</td></tr>
            )}
          </tbody>
        </table>
        </div>
        <Pagination page={page} totalPages={totalPages} onPageChange={(p) => { setPage(p); load(p); }} />
      </div>

      {detail && (
        <div className="fixed inset-0 z-40 bg-black/40 flex items-center justify-center p-4 overflow-y-auto" onClick={() => setDetail(null)}>
          <div className="card w-full max-w-2xl p-6 my-8" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-surface-900">Detail Penilaian</h2>
              <button onClick={() => setDetail(null)}><X className="w-5 h-5 text-surface-400" /></button>
            </div>
            <div className="space-y-3 text-sm">
              <p><span className="font-semibold">Siswa:</span> {detail.nama_siswa} ({detail.nisn}) - {detail.kelas}/{detail.jurusan}</p>
              <p><span className="font-semibold">Soal:</span> {detail.pertanyaan}</p>
              <p><span className="font-semibold">Jawaban:</span> {detail.jawaban_teks || <em>kosong</em>}</p>
              <p><span className="font-semibold">Knowledge Base:</span> {detail.knowledge_base_terkait?.join(', ')}</p>
              <div className="grid grid-cols-3 gap-3 py-2">
                <div className="card p-3 text-center"><p className="text-xs text-surface-500">Semantic Raw</p><p className="font-bold">{detail.semantic_raw?.toFixed(4)}</p></div>
                <div className="card p-3 text-center"><p className="text-xs text-surface-500">Semantic Score</p><p className="font-bold">{detail.semantic_score?.toFixed(2)}</p></div>
                <div className="card p-3 text-center"><p className="text-xs text-surface-500">Concept Score</p><p className="font-bold">{detail.concept_score?.toFixed(2)}</p></div>
              </div>
              <div>
                <p className="font-semibold mb-1">Concept Unit</p>
                <ul className="space-y-1">
                  {detail.detail_cu?.map((d, i) => (
                    <li key={i} className={`flex justify-between px-3 py-1.5 rounded-lg text-xs ${d.detected ? 'bg-green-50 text-green-700' : 'bg-surface-50 text-surface-500'}`}>
                      <span>{d.konsep}</span><span>{(d.similarity * 100).toFixed(1)}%</span>
                    </li>
                  ))}
                </ul>
              </div>
              <p><span className="font-semibold">Relevance gate:</span> {detail.relevance_status} &middot; <span className="font-semibold">Kualitas teks:</span> {detail.text_quality_status} {detail.noise_penalty_applied && '(penalti diterapkan)'}</p>
              <p className="text-lg font-bold text-primary-700">Skor Akhir: {detail.final_score?.toFixed(2) ?? '-'}</p>
              <p className="text-surface-600 italic">{detail.feedback}</p>
            </div>
          </div>
        </div>
      )}
    </GuruLayout>
  );
}