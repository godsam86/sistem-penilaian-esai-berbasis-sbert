import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';

// Landing & Auth
import LandingPage from './pages/LandingPage';
import Login        from './pages/auth/Login';

// Guru pages
import GuruDashboard from './pages/guru/GuruDashboard';
import GuruKB        from './pages/guru/GuruKB';
import GuruSoal      from './pages/guru/GuruSoal';
import GuruUjian     from './pages/guru/GuruUjian';
import GuruHasil     from './pages/guru/GuruHasil';
import GuruProfile   from './pages/guru/GuruProfile';

// Admin pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminAkun      from './pages/admin/AdminAkun';
import AdminGuru      from './pages/admin/AdminGuru';
import AdminSiswa     from './pages/admin/AdminSiswa';
import AdminMasterData from './pages/admin/AdminMasterData';
import AdminPenilaian from './pages/admin/AdminPenilaian';
import AdminProfile   from './pages/admin/AdminProfile';

// Siswa pages
import SiswaDashboard  from './pages/siswa/SiswaDashboard';
import SiswaUjianList  from './pages/siswa/SiswaUjianList';
import SiswaUjian      from './pages/siswa/SiswaUjian';
import SiswaHasil      from './pages/siswa/SiswaHasil';
import SiswaHasilSiswa from './pages/siswa/SiswaHasilSiswa';
import SiswaRiwayat    from './pages/siswa/SiswaRiwayat';
import SiswaProfile    from './pages/siswa/SiswaProfile';

function RequireAuth({ children, role }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-8 h-8 border-4 border-green-200 border-t-green-600 rounded-full animate-spin" />
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (role && user.role !== role) {
    let target = '/';
    if (user.role === 'admin') target = '/admin/dashboard';
    else if (user.role === 'guru') target = '/guru/dashboard';
    else if (user.role === 'siswa') target = '/siswa/dashboard';
    return <Navigate to={target} replace />;
  }
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />

      {/* ── ADMIN ────────────────────────────────────────── */}
      <Route path="/admin/dashboard" element={
        <RequireAuth role="admin"><AdminDashboard /></RequireAuth>
      } />
      <Route path="/admin/akun" element={
        <RequireAuth role="admin"><AdminAkun /></RequireAuth>
      } />
      <Route path="/admin/guru" element={
        <RequireAuth role="admin"><AdminGuru /></RequireAuth>
      } />
      <Route path="/admin/siswa" element={
        <RequireAuth role="admin"><AdminSiswa /></RequireAuth>
      } />
      <Route path="/admin/master-data" element={
        <RequireAuth role="admin"><AdminMasterData /></RequireAuth>
      } />
      <Route path="/admin/penilaian" element={
        <RequireAuth role="admin"><AdminPenilaian /></RequireAuth>
      } />
      <Route path="/admin/profil" element={
        <RequireAuth role="admin"><AdminProfile /></RequireAuth>
      } />
      <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />

      {/* ── GURU ─────────────────────────────────────────── */}
      <Route path="/guru/dashboard" element={
        <RequireAuth role="guru"><GuruDashboard /></RequireAuth>
      } />
      <Route path="/guru/kb" element={
        <RequireAuth role="guru"><GuruKB /></RequireAuth>
      } />
      <Route path="/guru/soal" element={
        <RequireAuth role="guru"><GuruSoal /></RequireAuth>
      } />
      <Route path="/guru/ujian" element={
        <RequireAuth role="guru"><GuruUjian /></RequireAuth>
      } />
      <Route path="/guru/hasil" element={
        <RequireAuth role="guru"><GuruHasil /></RequireAuth>
      } />
      <Route path="/guru/profil" element={
        <RequireAuth role="guru"><GuruProfile /></RequireAuth>
      } />
      <Route path="/guru" element={<Navigate to="/guru/dashboard" replace />} />

      {/* ── SISWA ─────────────────────────────────────────── */}
      <Route path="/siswa/dashboard" element={
        <RequireAuth role="siswa"><SiswaDashboard /></RequireAuth>
      } />
      <Route path="/siswa/ujian" element={
        <RequireAuth role="siswa"><SiswaUjianList /></RequireAuth>
      } />
      <Route path="/siswa/ujian/:ujianId" element={
        <RequireAuth role="siswa"><SiswaUjian /></RequireAuth>
      } />
      <Route path="/siswa/hasil/:ujianId" element={
        <RequireAuth role="siswa"><SiswaHasil /></RequireAuth>
      } />
      <Route path="/siswa/riwayat" element={
        <RequireAuth role="siswa"><SiswaRiwayat /></RequireAuth>
      } />
      <Route path="/siswa/hasil" element={
        <RequireAuth role="siswa"><SiswaHasilSiswa /></RequireAuth>
      } />
      <Route path="/siswa/profil" element={
        <RequireAuth role="siswa"><SiswaProfile /></RequireAuth>
      } />
      <Route path="/siswa" element={<Navigate to="/siswa/dashboard" replace />} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
