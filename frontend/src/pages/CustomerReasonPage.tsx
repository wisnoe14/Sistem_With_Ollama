import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

const topicLabelMap: Record<string, string> = {
  telecollection: "Telecollection (Penagihan & Recovery)",
  retention: "Retention (Pencegahan Churn)",
  winback: "Winback (Reaktivasi Customer)"
};

const CustomerReasonPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { customerName, customerId, topic, alasan } = location.state || {};
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 py-8 px-2">
      <div className="w-full max-w-xl bg-white p-8 rounded-3xl shadow-2xl border border-gray-100 space-y-8 animate-fade-in-down">
        <div className="flex flex-col items-center mb-6">
          <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-full p-4 shadow-lg mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2zm0 0c0 1.104.896 2 2 2s2-.896 2-2-.896-2-2-2-2 .896-2 2zm0 0v2m0 4h.01" /></svg>
          </div>
          <h2 className="text-3xl font-extrabold text-gray-800 mb-1 tracking-tight">Data Pelanggan</h2>
          <p className="text-gray-500 text-base">Berikut detail pelanggan yang tidak dapat dihubungi</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-blue-50 rounded-xl p-5 flex flex-col gap-1 border border-blue-100">
            <span className="text-xs text-gray-500 font-medium">Nama Pelanggan</span>
            <span className="text-lg font-bold text-blue-900">{customerName || '-'}</span>
          </div>
          <div className="bg-blue-50 rounded-xl p-5 flex flex-col gap-1 border border-blue-100">
            <span className="text-xs text-gray-500 font-medium">ID Pelanggan</span>
            <span className="text-lg font-bold text-blue-900">{customerId || '-'}</span>
          </div>
          <div className="bg-purple-50 rounded-xl p-5 flex flex-col gap-1 border border-purple-100">
            <span className="text-xs text-gray-500 font-medium">Topik Simulasi</span>
            <span className="text-lg font-bold text-purple-900">{topicLabelMap[topic] || topic}</span>
          </div>
          <div className="bg-red-50 rounded-xl p-5 flex flex-col gap-1 border border-red-100">
            <span className="text-xs text-gray-500 font-medium">Alasan Tidak Dapat Dihubungi</span>
            <span className="text-lg font-bold text-red-900">{alasan}</span>
          </div>
        </div>
        <div className="flex flex-col gap-4 mt-4">
          <button
            onClick={() => navigate('/Dashboard')}
            className="w-full py-3 bg-gradient-to-r from-gray-400 to-gray-600 hover:from-gray-500 hover:to-gray-700 text-white font-bold rounded-xl shadow-lg text-lg transition-all"
          >
            Kembali 
          </button>
        </div>
      </div>
    </div>
  );
};

export default CustomerReasonPage;
