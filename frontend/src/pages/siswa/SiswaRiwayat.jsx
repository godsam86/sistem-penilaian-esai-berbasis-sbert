import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SiswaLayout from '../../components/siswa/SiswaLayout';
import api from '../../utils/api';
import { SkeletonRows } from '../../components/common/Loading';

export default function SiswaRiwayat() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/jawaban/riwayat/').then(({ data }) => setList(data)).finally(() => setLoading(false));
  }, []);

  // Kelompokkan per ujian.
  const byUjian = list.reduce((acc, j) => {
    (acc[j.ujian] = acc[j.ujian] || []).push(j);
    return acc;
  }, {});

  return (
    <SiswaLayout title="Riwayat Ujian">
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-surface-50 text-left text-xs font-semibold uppercase text-surface-500">
            <tr>
              <th className="px-5 py-3">Ujian</th>
              <th className="px-5 py-3">Jumlah Soal Dijawab</th>
              <th className="px-5 py-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-100">
            {loading ? <SkeletonRows cols={3} /> : Object.entries(byUjian).map(([ujianId, jawaban]) => (
              <tr key={ujianId}>
                <td className="px-5 py-3 font-medium text-surface-800">{jawaban[0].pertanyaan ? `Ujian #${ujianId}` : ujianId}</td>
                <td className="px-5 py-3">{jawaban.length}</td>
                <td className="px-5 py-3 text-right">
                  <Link to={`/siswa/hasil/${ujianId}`} className="text-primary-600 hover:underline text-xs">Lihat Hasil</Link>
                </td>
              </tr>
            ))}
            {!loading && list.length === 0 && (
              <tr><td colSpan={3} className="px-5 py-8 text-center text-surface-400">Belum ada riwayat ujian.</td></tr>
            )}
          </tbody>
        </table>
        </div>
      </div>
    </SiswaLayout>
  );
}