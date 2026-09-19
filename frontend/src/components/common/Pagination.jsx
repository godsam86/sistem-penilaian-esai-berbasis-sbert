import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between gap-3 border-t border-surface-100 px-5 py-3 sm:px-6">
      <p className="text-xs text-surface-500">
        Halaman {page} dari {totalPages}
      </p>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          className="flex items-center gap-1 rounded-lg border border-surface-200 px-3 py-2 text-xs font-semibold text-surface-600 transition-colors hover:bg-surface-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <ChevronLeft className="h-4 w-4" /> Sebelumnya
        </button>
        <div className="flex items-center gap-1">
          {Array.from({ length: totalPages }, (_, index) => index + 1).map(pageNumber => (
            <button
              key={pageNumber}
              type="button"
              onClick={() => onPageChange(pageNumber)}
              aria-current={pageNumber === page ? 'page' : undefined}
              className={`min-w-8 rounded-lg border px-2.5 py-2 text-xs font-semibold transition-colors ${
                pageNumber === page
                  ? 'border-primary-600 bg-primary-600 text-white'
                  : 'border-surface-200 text-surface-600 hover:bg-surface-50'
              }`}
            >
              {pageNumber}
            </button>
          ))}
        </div>
        <button
          type="button"
          onClick={() => onPageChange(page + 1)}
          disabled={page === totalPages}
          className="flex items-center gap-1 rounded-lg border border-primary-200 bg-primary-50 px-3 py-2 text-xs font-semibold text-primary-700 transition-colors hover:bg-primary-100 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Berikutnya <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
