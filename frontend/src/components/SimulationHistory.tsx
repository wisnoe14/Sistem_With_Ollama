import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as XLSX from "xlsx";

interface HistoryItem {
  tanggal: string;
  customer_id: string;
  nama: string;
  topik: string;
  status: string;
  alasan: string;
}

interface SimulationHistoryProps {
  history: HistoryItem[];
}

export const SimulationHistory: React.FC<SimulationHistoryProps> = ({ history }) => {
  const tableRef = useRef<HTMLTableElement>(null);
  const [selectedResult, setSelectedResult] = useState<any | null>(null);

  const handleExport = () => {
    const table = tableRef.current;
    if (!table) return;
    const ws = XLSX.utils.table_to_sheet(table);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "History");
    XLSX.writeFile(wb, "simulation_history.xlsx");
  };

  const navigate = useNavigate();
  function handleDetail(idx: number) {
    const item = history[idx];
    if (item) {
      navigate('/detail-pelanggan', { state: { detail: item } });
    }
  }

  function closeModal() {
    setSelectedResult(null);
  }

  return (
    <div className="mt-6">
      {history.length === 0 ? (
        <div className="text-gray-400 text-center py-8">Belum ada riwayat simulasi.</div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
          <div className="flex justify-between items-center px-4 pt-4 pb-2">
            <span className="font-bold text-lg text-gray-700">Riwayat</span>
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg text-sm transition-colors shadow-md"
              disabled={history.length === 0}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4" /></svg>
              Download Excel
            </button>
          </div>
          <table ref={tableRef} className="min-w-full text-sm text-left text-gray-700 border-t border-gray-200">
            <thead className="bg-gray-100 sticky top-0 z-10">
              <tr>
                <th className="py-3 px-4 text-left font-bold border-b border-gray-200">TANGGAL</th>
                <th className="py-3 px-4 text-left font-bold border-b border-gray-200">CUSTOMER ID</th>
                <th className="py-3 px-4 text-left font-bold border-b border-gray-200">NAMA</th>
                <th className="py-3 px-4 text-left font-bold border-b border-gray-200">TOPIK</th>
                <th className="py-3 px-4 text-left font-bold border-b border-gray-200">STATUS</th>
                <th className="py-3 px-4 text-left font-bold border-b border-gray-200">ALASAN</th>
                <th className="py-3 px-4 text-left font-bold border-b border-gray-200">AKSI</th>
              </tr>
            </thead>
            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-4 px-4 text-center text-gray-500">
                    Tidak ada data riwayat simulasi.
                  </td>
                </tr>
              ) : (
                history.map((item, idx) => (
                  <tr
                    key={idx}
                    className={
                      idx % 2 === 0 ? "bg-white border-b border-gray-200" : "bg-gray-50 border-b border-gray-200"
                    }
                  >
                    <td className="py-3 px-4 align-top whitespace-pre-line font-medium">{item.tanggal}</td>
                    <td className="py-3 px-4 align-top">{item.customer_id}</td>
                    <td className="py-3 px-4 align-top">{item.nama}</td>
                    <td className="py-3 px-4 align-top">{item.topik}</td>
                    <td className="py-3 px-4 align-top">{item.status}</td>
                    <td className="py-3 px-4 align-top">{item.alasan}</td>
                    <td className="py-3 px-4 align-top">
                      <button
                        onClick={() => handleDetail(idx)}
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow"
                      >
                        Detail
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
          {/* Modal untuk menampilkan detail result */}
          {selectedResult && (
            <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
              <div className="bg-white rounded-xl shadow-2xl p-8 max-w-lg w-full relative">
                <button onClick={closeModal} className="absolute top-2 right-2 text-gray-500 hover:text-red-600 text-xl font-bold">&times;</button>
                <h3 className="text-lg font-bold mb-4 text-gray-800">Detail Hasil Simulasi</h3>
                <pre className="bg-gray-100 rounded p-4 text-xs text-gray-700 overflow-x-auto max-h-96">{JSON.stringify(selectedResult, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
