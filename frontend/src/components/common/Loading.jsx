import { Loader2 } from 'lucide-react';

/**
 * Full-screen overlay saat ada proses panjang seperti submit jawaban.
 */
export function LoadingOverlay({ show, message = 'Memproses...', sub = '' }) {
  if (!show) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl px-10 py-8 flex flex-col items-center gap-4 max-w-xs mx-4">
        <div className="relative">
          <div className="w-14 h-14 border-4 border-primary-200 rounded-full" />
          <div className="absolute inset-0 w-14 h-14 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
        <div className="text-center">
          <p className="font-bold text-surface-900 text-sm">{message}</p>
          {sub && <p className="text-surface-500 text-xs mt-1">{sub}</p>}
        </div>
      </div>
    </div>
  );
}

/**
 * Skeleton loader untuk baris tabel.
 */
export function SkeletonRows({ rows = 4, cols = 4 }) {
  return (
    <>
      {[...Array(rows)].map((_, i) => (
        <tr key={i}>
          {[...Array(cols)].map((_, j) => (
            <td key={j} className="px-5 py-3">
              <div className="h-4 bg-surface-200 rounded animate-pulse" style={{ width: `${60 + (j * 10) % 30}%` }} />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

/**
 * Card skeleton untuk grid stats.
 */
export function SkeletonCard() {
  return (
    <div className="card p-5">
      <div className="w-10 h-10 bg-surface-200 rounded-xl animate-pulse mb-3" />
      <div className="h-7 w-16 bg-surface-200 rounded animate-pulse mb-1.5" />
      <div className="h-3 w-24 bg-surface-100 rounded animate-pulse" />
    </div>
  );
}

/**
 * Inline spinner kecil.
 */
export function Spinner({ size = 'sm', className = '' }) {
  const s = size === 'sm' ? 'w-4 h-4' : size === 'md' ? 'w-6 h-6' : 'w-8 h-8';
  return <Loader2 className={`${s} animate-spin text-primary-500 ${className}`} />;
}
