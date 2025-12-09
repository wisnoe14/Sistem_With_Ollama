import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

const DetailDataPelanggan: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { detail } = location.state || {};

  if (!detail) {
    return (
      <div className="min-h-screen bg-gray-100 py-8 px-2 flex flex-col items-center">
        <div className="w-full max-w-2xl bg-white p-8 rounded-3xl shadow-2xl border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Detail Data Pelanggan</h2>
          <p className="text-red-500">Data tidak ditemukan.</p>
          <button
            onClick={() => navigate('/customer-simulation-history')}
            className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
          >
            Kembali ke Riwayat
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-2 flex flex-col items-center">
      <div className="w-full max-w-2xl bg-white p-8 rounded-3xl shadow-2xl border border-gray-100 space-y-6 animate-fade-in-down">
        <div className="flex flex-col items-center mb-6">
          <h2 className="text-3xl font-extrabold text-gray-800 mb-1 tracking-tight">Detail Data Pelanggan</h2>
          <p className="text-gray-500 text-base">Informasi lengkap hasil simulasi</p>
        </div>

        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center">
            <div className="w-full sm:w-1/3 font-semibold text-gray-700 mb-1 sm:mb-0">Tanggal:</div>
            <div className="w-full sm:w-2/3 text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">
              {detail.tanggal || '-'}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center">
            <div className="w-full sm:w-1/3 font-semibold text-gray-700 mb-1 sm:mb-0">Customer ID:</div>
            <div className="w-full sm:w-2/3 text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">
              {detail.customer_id || '-'}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center">
            <div className="w-full sm:w-1/3 font-semibold text-gray-700 mb-1 sm:mb-0">Nama Pelanggan:</div>
            <div className="w-full sm:w-2/3 text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">
              {detail.nama || '-'}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center">
            <div className="w-full sm:w-1/3 font-semibold text-gray-700 mb-1 sm:mb-0">Topik Simulasi:</div>
            <div className="w-full sm:w-2/3 text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">
              {detail.topik || '-'}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center">
            <div className="w-full sm:w-1/3 font-semibold text-gray-700 mb-1 sm:mb-0">Status:</div>
            <div className="w-full sm:w-2/3 text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">
              <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                detail.status?.includes('Bisa') ? 'bg-green-100 text-green-800' : 
                detail.status?.includes('Tidak') ? 'bg-red-100 text-red-800' : 
                'bg-gray-100 text-gray-800'
              }`}>
                {detail.status || '-'}
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center">
            <div className="w-full sm:w-1/3 font-semibold text-gray-700 mb-1 sm:mb-0">Alasan:</div>
            <div className="w-full sm:w-2/3 text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">
              {detail.alasan || '-'}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center">
            <div className="w-full sm:w-1/3 font-semibold text-gray-700 mb-1 sm:mb-0">Estimasi Bayar:</div>
            <div className="w-full sm:w-2/3 text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">
              <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                detail.estimasi_pembayaran?.includes('Hari ini') ? 'bg-green-100 text-green-800' :
                detail.estimasi_pembayaran?.includes('Besok') ? 'bg-yellow-100 text-yellow-800' :
                detail.estimasi_pembayaran?.includes('Belum') ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {detail.estimasi_pembayaran || '-'}
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center">
            <div className="w-full sm:w-1/3 font-semibold text-gray-700 mb-1 sm:mb-0">Indikator Risiko:</div>
            <div className="w-full sm:w-2/3 text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">
              {detail.risk_level && detail.risk_label && detail.risk_color ? (
                <span 
                  className="inline-block px-3 py-1 text-sm font-semibold text-white rounded-full"
                  style={{ backgroundColor: detail.risk_color }}
                >
                  {detail.risk_label}
                </span>
              ) : (
                <span className="text-gray-400">-</span>
              )}
            </div>
          </div>
        </div>

        <div className="flex justify-center mt-8">
          <button
            onClick={() => navigate('/menu-riwayat-simulasi')}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-colors shadow-lg"
          >
            Kembali ke Riwayat Simulasi
          </button>
        </div>
      </div>
    </div>
  );
};

export default DetailDataPelanggan;