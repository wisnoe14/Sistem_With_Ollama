import React from "react";
import { useNavigate } from "react-router-dom";
import * as XLSX from "xlsx";

const CustomerSimulationHistoryMenu: React.FC = () => {
  const navigate = useNavigate();
  const historyRaw = localStorage.getItem("simulationHistory");
  const history = historyRaw ? JSON.parse(historyRaw) : [];

  const handleExport = () => {
    const worksheetData = history.map((item: any) => ({
      Tanggal: item.tanggal || item.date,
      "Customer ID": item.customer_id || item.result?.customer_id || '-',
      Nama: item.nama || item.result?.customer_name || sessionStorage.getItem('customer_name') || '-',
      Topik: item.topik || item.topic || '-',
      Status: item.status || item.result?.status || '-',
      Alasan: item.alasan || item.result?.alasan || '-',
      "Estimasi Bayar": item.estimasi_pembayaran || item.result?.estimasi_pembayaran || '-'
    }));
    const worksheet = XLSX.utils.json_to_sheet(worksheetData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Riwayat Simulasi");
    XLSX.writeFile(workbook, "Riwayat_Simulasi_CS.xlsx");
  };

  const handleReset = () => {
    if (window.confirm('Apakah Anda yakin ingin menghapus seluruh riwayat simulasi?')) {
      localStorage.removeItem('simulationHistory');
      window.location.reload();
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-2 flex flex-col items-center">
      <div className="w-full max-w-4xl bg-white p-8 rounded-3xl shadow-2xl border border-gray-100 space-y-8 animate-fade-in-down">
        <div className="flex flex-col items-center mb-6">
          <h2 className="text-3xl font-extrabold text-gray-800 mb-1 tracking-tight">Menu Riwayat Simulasi Pelanggan</h2>
          <p className="text-gray-500 text-base">Data hasil simulasi pelanggan (bisa dihubungi & tidak bisa dihubungi)</p>
        </div>
        <div className="flex flex-col sm:flex-row justify-between items-center mb-4 gap-4">
          <div className="flex gap-2">
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-700 text-white font-semibold rounded-lg text-sm transition-colors shadow-md"
              disabled={history.length === 0}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              Reset
            </button>
          </div>
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg text-sm transition-colors shadow-md"
            disabled={history.length === 0}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4" /></svg>
            Ekspor ke Excel
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-600">
            <thead className="text-xs text-gray-700 uppercase bg-gray-100">
              <tr>
                <th className="px-4 py-3">Tanggal</th>
                <th className="px-4 py-3">Customer ID</th>
                <th className="px-4 py-3">Nama</th>
                <th className="px-4 py-3">Topik</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Alasan</th>
                <th className="px-4 py-3">Estimasi Bayar</th>
                <th className="px-4 py-3">Aksi</th>
              </tr>
            </thead>
            {history.length > 0 ? (
              <tbody>
                {history.map((item: any, idx: number) => (
                  <tr key={idx} className="bg-white border-b hover:bg-gray-50">
                    <td className="px-4 py-3">{item.tanggal || item.date || '-'}</td>
                    <td className="px-4 py-3">{item.customer_id || item.result?.customer_id || '-'}</td>
                    <td className="px-4 py-3">{item.nama || item.result?.customer_name || sessionStorage.getItem('customer_name') || '-'}</td>
                    <td className="px-4 py-3">{item.topik || item.topic || '-'}</td>
                    <td className="px-4 py-3">{item.status || item.result?.status || '-'}</td>
                    <td className="px-4 py-3">{item.alasan || item.result?.alasan || '-'}</td>
                    <td className="px-4 py-3">{item.estimasi_pembayaran || item.result?.estimasi_pembayaran || '-'}</td>
                    <td className="px-4 py-3">
                      <button
                        className="px-3 py-1 bg-blue-600 text-white rounded text-xs font-semibold hover:bg-blue-700 transition-all"
                        onClick={() => navigate('/detail-pelanggan', { state: { detail: {
                          customer_id: item.customer_id || item.result?.customer_id || '-',
                          nama: item.nama || item.result?.customer_name || sessionStorage.getItem('customer_name') || '-',
                          topik: item.topik || item.topic || '-',
                          status: item.status || item.result?.status || '-',
                          alasan: item.alasan || item.result?.alasan || '-',
                          estimasi_pembayaran: item.estimasi_pembayaran || item.result?.estimasi_pembayaran || '-',
                          tanggal: item.tanggal || item.date || '-'
                        } } })}
                      >
                        Detail
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            ) : (
              <tbody>
                <tr>
                  <td colSpan={8} className="text-center py-4">Tidak ada data riwayat simulasi.</td>
                </tr>
              </tbody>
            )}
          </table>
        </div>
        <div className="flex justify-end mt-4">
          <button onClick={() => navigate('/Home')} className="px-6 py-2 bg-gray-400 hover:bg-gray-600 text-white rounded-xl font-bold">Kembali ke Input ID</button>

        </div>
      </div>
    </div>
  );
};

export default CustomerSimulationHistoryMenu;

