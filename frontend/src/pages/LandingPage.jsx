import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { SCHOOL_NAME, SCHOOL_LOGO_URL } from '../branding';

export default function LandingPage() {
  const navigate = useNavigate();
  const [scrolled,  setScrolled]  = useState(false);
  const [menuOpen,  setMenuOpen]  = useState(false);
  const [stats,     setStats]     = useState({
    totalPenilaian: 0,
    totalChunk:     0,
  });

  // Sticky navbar
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Ambil statistik dari backend
  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Total penilaian yang sudah selesai
        const [penilaianRes, chunkRes] = await Promise.allSettled([
          api.get('/public/stats'),
          api.get('/public/stats'),
        ]);

        let totalPenilaian = 0;
        let totalChunk     = 0;

        if (penilaianRes.status === 'fulfilled') {
          totalPenilaian = penilaianRes.value.data?.total_penilaian || 0;
        }
        if (chunkRes.status === 'fulfilled') {
          totalChunk = chunkRes.value.data?.total_chunk || 0;
        }

        setStats({ totalPenilaian, totalChunk });
      } catch (_) {
        // Jika endpoint belum ada, tampilkan 0 saja (tidak crash)
      }
    };
    fetchStats();
  }, []);

  const scrollTo = (id) => {
    setMenuOpen(false);
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-white font-sans overflow-x-hidden">

      {/* ── NAVBAR ───────────────────────────────────────────── */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300
        ${scrolled ? 'bg-white/95 backdrop-blur shadow-sm' : 'bg-white/80 backdrop-blur'}`}>
        <div className="max-w-6xl mx-auto px-5 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <img src={SCHOOL_LOGO_URL} alt="Logo" className="w-8 h-8 rounded-lg object-cover" />
            <div>
              <p className="text-sm font-extrabold text-gray-900 leading-tight">{SCHOOL_NAME}</p>
              <p className="text-xs text-violet-500 leading-tight">Sistem Penilaian Esai Otomatis</p>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-8">
            {[['Beranda','hero'],['Fitur','fitur'],['Cara Kerja','cara-kerja'],['Tentang','tentang'],['Kontak','kontak']].map(([label,id]) => (
              <button key={id} onClick={() => scrollTo(id)}
                className="text-sm text-gray-600 hover:text-violet-600 font-medium transition-colors">
                {label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <button className="md:hidden p-2 rounded-lg hover:bg-gray-100" onClick={() => setMenuOpen(v => !v)}>
              <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {menuOpen
                  ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />}
              </svg>
            </button>
          </div>
        </div>
        {menuOpen && (
          <div className="md:hidden bg-white border-t border-gray-100 px-5 py-4 space-y-3">
            {[['Beranda','hero'],['Fitur','fitur'],['Cara Kerja','cara-kerja'],['Tentang','tentang'],['Kontak','kontak']].map(([label,id]) => (
              <button key={id} onClick={() => scrollTo(id)}
                className="block text-sm text-gray-700 hover:text-violet-600 font-medium py-1">
                {label}
              </button>
            ))}
          </div>
        )}
      </nav>

      {/* ── HERO ─────────────────────────────────────────────── */}
      <section id="hero" className="pt-24 pb-20 px-5">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-violet-50 border border-violet-200 text-violet-600 text-xs font-semibold px-3.5 py-1.5 rounded-full mb-6">
                <span className="text-base">✨</span>
                Ditenagai AI Ramah!
              </div>
              <h1 className="text-5xl sm:text-6xl font-black text-gray-900 leading-tight mb-5">
                Sistem<br/>
                <span className="text-violet-600">Penilaian</span>
              </h1>
              <p className="text-gray-500 text-base leading-relaxed mb-8 max-w-md">
                Nilai jawaban esai secara otomatis menggunakan kecerdasan buatan. Hasilnya akurat, adil, dan siswa langsung tahu apa yang perlu diperbaiki! 🚀
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <button onClick={() => navigate('/login')}
                  className="flex items-center justify-center gap-2 px-7 py-3.5 bg-gray-900 text-white text-sm font-bold rounded-2xl hover:bg-gray-700 transition-all shadow-lg shadow-gray-900/20">
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                  Login Siswa
                </button>
                <button onClick={() => scrollTo('cara-kerja')}
                  className="flex items-center justify-center gap-2 px-7 py-3.5 border border-gray-200 text-gray-700 text-sm font-semibold rounded-2xl hover:bg-gray-50 transition-all">
                  Lihat Cara Kerja
                </button>
              </div>
            </div>

            {/* Rapor AI Card */}
            <div className="flex justify-center lg:justify-end">
              <div className="relative w-full max-w-sm">
                <div className="absolute -inset-8 bg-gradient-to-br from-violet-100 via-pink-50 to-cyan-50 rounded-full blur-3xl opacity-60" />
                <div className="relative bg-white rounded-3xl shadow-2xl shadow-violet-100 p-6 border border-gray-100">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 bg-violet-100 rounded-lg flex items-center justify-center">
                        <svg className="w-3.5 h-3.5 text-violet-600" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M2 4a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H3a1 1 0 01-1-1V4zM2 9a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H3a1 1 0 01-1-1V9zM13 9a1 1 0 00-1 1v6a1 1 0 001 1h4a1 1 0 001-1v-6a1 1 0 00-1-1h-4z"/>
                        </svg>
                      </div>
                      <span className="text-sm font-bold text-gray-900">Rapor AI</span>
                    </div>
                    <span className="flex items-center gap-1.5 bg-emerald-50 text-emerald-600 text-xs font-bold px-2.5 py-1 rounded-full">
                      <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                      Aktif
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mb-5">
                    {/* FIX: Total Esai Diperiksa dari API */}
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Esai Diperiksa</p>
                      <p className="text-2xl font-black text-violet-600">
                        {stats.totalPenilaian > 0 ? stats.totalPenilaian.toLocaleString('id-ID') : '—'}
                      </p>
                      <p className="text-xs text-emerald-500 font-semibold mt-0.5">
                        {stats.totalPenilaian > 0 ? '✓ Sudah dinilai' : 'Belum ada data'}
                      </p>
                    </div>
                    {/* FIX: Total Chunk KB */}
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Total Chunk KB</p>
                      <p className="text-2xl font-black text-pink-500">
                        {stats.totalChunk > 0 ? stats.totalChunk.toLocaleString('id-ID') : '—'}
                      </p>
                      <p className="text-xs text-pink-400 font-semibold mt-0.5">
                        {stats.totalChunk > 0 ? '📚 Materi aktif' : 'Belum ada KB'}
                      </p>
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-2xl p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-violet-600 rounded-xl flex items-center justify-center text-white font-black text-xs leading-tight text-center p-1">
                          SBERT
                        </div>
                        <div>
                          <p className="text-xs font-bold text-gray-800">Kemiripan Semantik</p>
                          <p className="text-xs text-gray-400">Sentence-BERT</p>
                        </div>
                      </div>
                      <span className="text-sm font-black text-gray-700">80%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="h-2 rounded-full bg-gradient-to-r from-pink-400 to-violet-500" style={{width:'80%'}} />
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    {['Akurat','Cepat','Adil'].map(t => (
                      <span key={t} className="flex-1 text-center text-xs font-semibold py-1.5 rounded-xl bg-violet-50 text-violet-600">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── STATS BAR ─────────────────────────────────────────── */}
      <section className="py-8 bg-gray-50 border-y border-gray-100">
        <div className="max-w-6xl mx-auto px-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {/* FIX card pertama: Concept Units dengan penjelasan */}
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 bg-white rounded-2xl flex items-center justify-center text-xl shadow-sm border border-gray-100 shrink-0">
                🧩
              </div>
              <div>
                <p className="text-xl font-black text-violet-600">Concept Units</p>
                <p className="text-xs text-gray-400 font-medium leading-tight">
                  Konsep penting jawaban referensi sebagai dasar penilaian kelengkapan
                </p>
              </div>
            </div>
            {/* FIX card kedua: Total esai dari API */}
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 bg-white rounded-2xl flex items-center justify-center text-xl shadow-sm border border-gray-100 shrink-0">
                📝
              </div>
              <div>
                <p className="text-xl font-black text-pink-500">
                  {stats.totalPenilaian > 0 ? `${stats.totalPenilaian.toLocaleString('id-ID')}+` : '—'}
                </p>
                <p className="text-xs text-gray-400 font-medium">Esai Diperiksa</p>
              </div>
            </div>
            {/* FIX card ketiga: Total chunk */}
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 bg-white rounded-2xl flex items-center justify-center text-xl shadow-sm border border-gray-100 shrink-0">
                📚
              </div>
              <div>
                <p className="text-xl font-black text-cyan-500">
                  {stats.totalChunk > 0 ? `${stats.totalChunk.toLocaleString('id-ID')}` : '—'}
                </p>
                <p className="text-xs text-gray-400 font-medium">Total Chunk KB</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 bg-white rounded-2xl flex items-center justify-center text-xl shadow-sm border border-gray-100 shrink-0">
                🤖
              </div>
              <div>
                <p className="text-xl font-black text-violet-600">SBERT</p>
                <p className="text-xs text-gray-400 font-medium">Model AI Penilaian</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FITUR ────────────────────────────────────────────── */}
      <section id="fitur" className="py-20 px-5">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <span className="text-xs font-bold text-violet-500 uppercase tracking-widest">Fitur Unggulan</span>
            <h2 className="text-3xl font-black text-gray-900 mt-2">Kenapa Sistem Ini?</h2>
            <p className="text-gray-500 mt-3 max-w-xl mx-auto text-sm">Teknologi NLP terkini untuk penilaian esai Bahasa Indonesia yang lebih cerdas dan efisien.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon:'⚡', color:'bg-violet-50', title:'Penilaian Instan', desc:'Begitu siswa klik kirim, jawaban langsung dinilai secara otomatis. Tidak perlu menunggu berhari-hari.' },
              { icon:'🧠', color:'bg-pink-50',   title:'Memahami Makna', desc:'Menggunakan Sentence-BERT yang memahami makna kalimat, sehingga jawaban dengan sinonim tetap dinilai tepat.' },
              { icon:'📊', color:'bg-cyan-50',   title:'Feedback Langsung', desc:'Siswa langsung tahu konsep mana yang sudah dikuasai dan mana yang perlu dipelajari lebih lanjut.' },
              { icon:'🎯', color:'bg-emerald-50',title:'Concept Units', desc:'Guru mendefinisikan konsep-konsep kunci jawaban. Sistem otomatis mengukur kelengkapan konsep dalam jawaban siswa.' },
              { icon:'📚', color:'bg-orange-50', title:'Materi Fleksibel', desc:'Guru bisa upload atau perbarui materi referensi kapan saja. Sistem langsung menyesuaikan tanpa perlu diatur ulang.' },
              { icon:'🔒', color:'bg-violet-50', title:'Akses Terpisah', desc:'Portal guru dan siswa dipisahkan dengan sistem login berbeda untuk menjaga keamanan soal dan data ujian.' },
            ].map(({ icon, color, title, desc }) => (
              <div key={title} className="bg-white rounded-3xl p-6 border border-gray-100 hover:shadow-lg hover:shadow-violet-50 hover:-translate-y-1 transition-all duration-300">
                <div className={`w-11 h-11 rounded-2xl flex items-center justify-center text-xl mb-4 ${color}`}>
                  {icon}
                </div>
                <h3 className="font-bold text-gray-900 mb-2 text-sm">{title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CARA KERJA + BAGIAN NILAI ───────────────────────── */}
      <section id="cara-kerja" className="py-20 px-5 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">

            {/* FIX: Cara Kerja dengan teks yang lebih wajar */}
            <div>
              <div className="flex items-center gap-2 mb-8">
                <span className="text-xl">🔄</span>
                <h2 className="text-2xl font-black text-gray-900">Cara Kerjanya</h2>
              </div>
              <div className="space-y-4">
                {[
                  { n:'1', icon:'📝', label:'Tulis Jawaban',    sub:'Ketik langsung atau upload file', color:'bg-violet-100 text-violet-600' },
                  { n:'2', icon:'✨', label:'Pembersihan Teks', sub:'Sistem merapikan dan memproses teks', color:'bg-pink-100 text-pink-600' },
                  { n:'3', icon:'🧠', label:'Analisis Makna',   sub:'AI membaca dan memahami isi jawaban', color:'bg-cyan-100 text-cyan-600' },
                  { n:'4', icon:'🔍', label:'Pencocokan Materi',sub:'Jawaban dibandingkan dengan materi referensi', color:'bg-orange-100 text-orange-500' },
                  { n:'5', icon:'🏆', label:'Nilai Keluar',     sub:'Skor dan feedback langsung tampil', color:'bg-emerald-100 text-emerald-600' },
                ].map((step, i, arr) => (
                  <div key={step.n} className="flex items-center gap-4">
                    <div className="flex flex-col items-center">
                      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${step.color} shrink-0`}>
                        <span className="text-lg">{step.icon}</span>
                      </div>
                      {i < arr.length - 1 && <div className="w-0.5 h-5 bg-gray-200 mt-1" />}
                    </div>
                    <div>
                      <p className="text-sm font-bold text-gray-900">{step.n}. {step.label}</p>
                      <p className="text-xs text-gray-400">{step.sub}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Bagian Nilai */}
            <div>
              <div className="flex items-center gap-2 mb-8">
                <span className="text-xl">🎯</span>
                <h2 className="text-2xl font-black text-gray-900">Komponen Penilaian</h2>
              </div>
              <div className="space-y-4">
                {[
                  {
                    label:'Kemiripan Semantik (80%)', pct:80,
                    color:'bg-violet-500', light:'bg-violet-50', text:'text-violet-600',
                    desc:'Mengukur seberapa mirip makna jawaban siswa dengan materi referensi menggunakan Sentence-BERT.',
                    icon:'💡'
                  },
                  {
                    label:'Kelengkapan Konsep (20%)', pct:20,
                    color:'bg-pink-500', light:'bg-pink-50', text:'text-pink-600',
                    desc:'Konsep-konsep penting pada jawaban referensi digunakan sebagai dasar untuk menilai kelengkapan jawaban siswa.',
                    icon:'🧩'
                  },
                ].map(({ label, pct, color, light, text, desc, icon }) => (
                  <div key={label} className="bg-white rounded-2xl p-5 border border-gray-100 hover:shadow-md transition-all">
                    <div className="flex items-start gap-3 mb-3">
                      <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${light} shrink-0`}>
                        <span className="text-base">{icon}</span>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-0.5">
                          <p className={`text-sm font-bold ${text}`}>{label}</p>
                          <span className={`text-sm font-black ${text}`}>{pct}%</span>
                        </div>
                        <p className="text-xs text-gray-400 leading-relaxed">{desc}</p>
                      </div>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div className={`h-2 rounded-full ${color}`} style={{width:`${pct}%`}} />
                    </div>
                  </div>
                ))}

                {/* Formula box */}
                <div className="bg-gradient-to-r from-violet-600 to-pink-500 rounded-2xl p-5 text-white">
                  <p className="text-xs font-bold opacity-80 mb-2">Rumus Skor Akhir</p>
                  <p className="font-black text-lg leading-tight">
                    (Kemiripan Semantik × 80%) +<br/>(Kelengkapan Konsep × 20%)
                  </p>
                  <p className="text-xs opacity-70 mt-2">Skala 0 – 100 poin</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── TENTANG ──────────────────────────────────────────── */}
      <section id="tentang" className="py-20 px-5">
        <div className="max-w-6xl mx-auto">
          <div className="bg-gradient-to-br from-violet-600 via-violet-500 to-pink-500 rounded-3xl p-10 md:p-14 text-white text-center relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/3" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/3" />
            <div className="relative">
              <span className="text-4xl mb-4 block">🎓</span>
              <h2 className="text-3xl font-black mb-4">Tentang Sistem Ini</h2>
              <p className="text-white/80 max-w-2xl mx-auto leading-relaxed mb-2">
                Sistem penilaian jawaban esai otomatis berbasis kecerdasan buatan yang dikembangkan untuk SMKN1 Pegagan Hilir.
              </p>
              <p className="text-white/80 max-w-2xl mx-auto leading-relaxed">
                Menggunakan teknologi <strong className="text-white">Sentence-BERT</strong> dan <strong className="text-white">Knowledge Base</strong> untuk menilai jawaban esai mata pelajaran Bahasa Indonesia secara semantik — memahami makna jawaban, bukan sekadar mencocokkan kata.
              </p>
              <div className="flex flex-wrap justify-center gap-3 mt-8">
                {['Sentence-BERT','Cosine Similarity','Knowledge Base','Concept Units','FastAPI','React'].map(t => (
                  <span key={t} className="bg-white/20 text-white text-xs font-semibold px-3 py-1.5 rounded-full border border-white/30">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── KONTAK ───────────────────────────────────────────── */}
      <section id="kontak" className="py-20 px-5 bg-gray-50">
        <div className="max-w-xl mx-auto text-center">
          <span className="text-xs font-bold text-violet-500 uppercase tracking-widest">Kontak</span>
          <h2 className="text-3xl font-black text-gray-900 mt-2 mb-4">Ada Pertanyaan?</h2>
          <p className="text-gray-500 text-sm mb-8">Hubungi guru atau administrator sekolah untuk mendapatkan akun dan informasi lebih lanjut.</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-white rounded-2xl p-5 border border-gray-100 text-left">
              <div className="w-9 h-9 bg-violet-50 rounded-xl flex items-center justify-center text-base mb-3">📍</div>
              <p className="text-xs font-bold text-gray-500 mb-1">Lokasi</p>
              <p className="text-sm font-semibold text-gray-900">SMKN1 Pegagan Hilir</p>
              <p className="text-xs text-gray-400">Kab. Dairi, Sumatera Utara</p>
            </div>
            <div className="bg-white rounded-2xl p-5 border border-gray-100 text-left">
              <div className="w-9 h-9 bg-pink-50 rounded-xl flex items-center justify-center text-base mb-3">🤖</div>
              <p className="text-xs font-bold text-gray-500 mb-1">Teknologi</p>
              <p className="text-sm font-semibold text-gray-900">AI Berbasis SBERT</p>
              <p className="text-xs text-gray-400">Multilingual NLP · Bahasa Indonesia</p>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 mt-8 justify-center">
            <button onClick={() => navigate('/login')}
              className="px-7 py-3.5 bg-gray-900 text-white text-sm font-bold rounded-2xl hover:bg-gray-700 transition-all shadow-lg">
              Login Siswa
            </button>
            <button onClick={() => navigate('/login')}
              className="px-7 py-3.5 border border-violet-300 text-violet-600 text-sm font-bold rounded-2xl hover:bg-violet-50 transition-all">
              Login Guru
            </button>
          </div>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────── */}
      <footer className="bg-gray-900 py-8 px-5">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <img src={SCHOOL_LOGO_URL} alt="Logo" className="w-7 h-7 rounded-lg object-cover" />
              <div>
                <p className="text-sm font-extrabold text-white leading-tight">{SCHOOL_NAME}</p>
                <p className="text-xs text-gray-400 leading-tight">Belajar Pintar, Nilai Cepat! ⭐</p>
              </div>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">© 2026 SMKN1 Pegagan Hilir. Dibuat dengan ❤️</p>
              <p className="text-xs text-violet-400 font-medium">SMKN1 Pegagan Hilir | AI by Sentence-BERT</p>
            </div>
            <div className="flex items-center gap-4">
              {['Pintar','Tepat','Cepat'].map(t => (
                <span key={t} className="flex items-center gap-1.5 text-xs text-gray-400 font-medium">
                  <span>{t === 'Pintar' ? '🎓' : t === 'Tepat' ? '🎯' : '⚡'}</span>
                  {t}
                </span>
              ))}
            </div>
          </div>
        </div>
      </footer>

    </div>
  );
}
