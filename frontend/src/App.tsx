import { BrowserRouter, Routes, Route, Link, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import PageTransition from "./components/PageTransition";
import CSSimulation from "./pages/CSSimulation";

import CustomerSimulationHistoryMenu from "./pages/CustomerSimulationHistoryMenu";
import ResultPage from "./pages/ResultPage";
import Home from "./pages/Home";
import LoginPage from "./pages/Login";
import QnAFlow from "./components/QnAFlow";
import CustomerReasonPage from "./pages/CustomerReasonPage";
import DetailDataPelanggan from "./pages/DetailDataPelanggan";
import type { ReactNode } from "react";


/**
 * Komponen untuk halaman 404 Not Found yang lebih profesional.
 */
const NotFound = () => (
  <div className="flex flex-col items-center justify-center min-h-screen bg-slate-100 text-slate-700 font-sans p-4">
    <div className="text-center">
      {/* Ikon SVG untuk visual */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="mx-auto h-24 w-24 text-sky-500 mb-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <h1 className="text-6xl font-extrabold text-sky-700">404</h1>
      <p className="text-2xl font-semibold mt-2 text-slate-800">Halaman Tidak Ditemukan</p>
      <p className="mt-4 text-slate-500">
        Maaf, kami tidak dapat menemukan halaman yang Anda cari.
      </p>
      <Link
        to="/"
        className="mt-8 inline-block bg-sky-600 hover:bg-sky-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-transform transform hover:-translate-y-1"
      >
        Kembali ke Halaman Utama
      </Link>
    </div>
  </div>
);

/**
 * Komponen utama aplikasi yang mengatur semua routing.
 */
export default function App() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [showChat, setShowChat] = useState(false);

  // Fungsi untuk delay dan set loading
  const handlePageChange = async (callback: () => void) => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1200)); // delay 1.2 detik
    callback();
    setLoading(false);
  };
  function RequireAuth({ children }: { children: ReactNode }) {
    const location = useLocation();
    const navigate = useNavigate();
    const token = sessionStorage.getItem('token');
    useEffect(() => {
      const isLoginPage = location.pathname === '/';
      if (!token && !isLoginPage) {
        navigate('/');
      }
    }, [location, navigate, token]);
    if (!token && location.pathname !== '/') {
      return null; // Jangan render children jika belum login
    }
    return <>{children}</>;
  }

  function RequireCustomerId({ children }: { children: ReactNode }) {
    const navigate = useNavigate();
    const customerId = sessionStorage.getItem('customer_id');
    useEffect(() => {
      if (!customerId) {
        navigate('/Home');
      }
    }, [customerId, navigate]);
    if (!customerId) {
      return null;
    }
    return <>{children}</>;
  }

  const handleStatus = async (value: string) => {
    const customer_id = sessionStorage.getItem('customer_id');
    await fetch('http://localhost:8000/api/v1/endpoints/conversation/update-status-dihubungi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_id, status: value }),
    });
    setStatus(value);
    setShowChat(true);
  };

  return (
    <BrowserRouter>
      <PageTransition show={loading} />
      <Routes>
        <Route path="/" element={
          <LoginPage onLoginSuccess={() => handlePageChange(() => {})} />
        } />
        <Route path="/Home" element={
          <RequireAuth>
            <Home onLoginSuccess={() => handlePageChange(() => {})} />
          </RequireAuth>
        } />
        <Route path="/Dashboard" element={
          <RequireAuth>
            <RequireCustomerId>
              <CSSimulation />
            </RequireCustomerId>
          </RequireAuth>
        } />
  <Route path="/result" element={<ResultPage />} />

  <Route path="/menu-riwayat-simulasi" element={<CustomerSimulationHistoryMenu />} />
        <Route path="/customer-reason" element={<CustomerReasonPage />} />
        <Route path="/detail-pelanggan" element={<DetailDataPelanggan />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
      {/* QnAFlow logic restored */}
    </BrowserRouter>
  );
}