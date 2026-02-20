import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

type ConversationHistoryItem = {
  tanggal: string;
  customer_id: string;
  nama: string;
  topic: string;
  question: string;
  answer: string;
};

const ConversationHistoryPage: React.FC = () => {
  const navigate = useNavigate();

  const conversationHistory: ConversationHistoryItem[] = useMemo(() => {
    try {
      const raw = localStorage.getItem('conversationHistory');
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A1D5A] via-[#112D84] to-[#0A1D5A] py-8 px-4">
      <div className="max-w-6xl mx-auto bg-white/95 border border-blue-200 rounded-3xl shadow-2xl p-6 md:p-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-800">Riwayat Percakapan</h1>
            <p className="text-slate-500 text-sm md:text-base">Log pertanyaan dan jawaban dari simulasi pelanggan</p>
          </div>
          <button
            onClick={() => navigate('/Home')}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
          >
            Kembali
          </button>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="min-w-full text-sm text-left text-slate-700">
            <thead className="bg-slate-100 text-slate-700 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Tanggal</th>
                <th className="px-4 py-3">Customer</th>
                <th className="px-4 py-3">Topik</th>
                <th className="px-4 py-3">Pertanyaan</th>
                <th className="px-4 py-3">Jawaban</th>
              </tr>
            </thead>
            <tbody>
              {conversationHistory.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-slate-500">Belum ada riwayat percakapan.</td>
                </tr>
              ) : (
                conversationHistory.map((item, idx) => (
                  <tr key={idx} className="border-t border-slate-200 hover:bg-slate-50 align-top">
                    <td className="px-4 py-3 whitespace-nowrap">{item.tanggal || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="font-semibold">{item.customer_id || '-'}</div>
                      <div className="text-xs text-slate-500">{item.nama || '-'}</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">{item.topic || '-'}</td>
                    <td className="px-4 py-3 min-w-[280px]">{item.question || '-'}</td>
                    <td className="px-4 py-3 min-w-[220px]">{item.answer || '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ConversationHistoryPage;
