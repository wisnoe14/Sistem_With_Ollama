import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

type SimulationHistoryItem = {
  topik?: string;
  status?: string;
  risk_label?: string;
};

type ConversationHistoryItem = {
  topic?: string;
};

const AnalyticsPage: React.FC = () => {
  const navigate = useNavigate();

  const simulationHistory: SimulationHistoryItem[] = useMemo(() => {
    try {
      const raw = localStorage.getItem('simulationHistory');
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }, []);

  const conversationHistory: ConversationHistoryItem[] = useMemo(() => {
    try {
      const raw = localStorage.getItem('conversationHistory');
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }, []);

  const topikStats = useMemo(() => {
    const counts: Record<string, number> = { telecollection: 0, retention: 0, winback: 0 };
    simulationHistory.forEach((item) => {
      const key = (item.topik || '').toLowerCase();
      if (counts[key] !== undefined) counts[key] += 1;
    });
    return counts;
  }, [simulationHistory]);

  const statusStats = useMemo(() => {
    let dihubungi = 0;
    let tidakDihubungi = 0;
    simulationHistory.forEach((item) => {
      const status = (item.status || '').toLowerCase();
      if (status.includes('tidak dihubungi')) tidakDihubungi += 1;
      else if (status) dihubungi += 1;
    });
    return { dihubungi, tidakDihubungi };
  }, [simulationHistory]);

  const riskStats = useMemo(() => {
    const counts: Record<string, number> = {};
    simulationHistory.forEach((item) => {
      const label = item.risk_label || 'Tidak diketahui';
      counts[label] = (counts[label] || 0) + 1;
    });
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  }, [simulationHistory]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A1D5A] via-[#112D84] to-[#0A1D5A] py-8 px-4">
      <div className="max-w-5xl mx-auto bg-white/95 border border-blue-200 rounded-3xl shadow-2xl p-6 md:p-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-800">Analytics Simulasi</h1>
            <p className="text-slate-500 text-sm md:text-base">Ringkasan data dari riwayat simulasi dan riwayat percakapan</p>
          </div>
          <button
            onClick={() => navigate('/Home')}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
          >
            Kembali
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <p className="text-xs text-slate-500">Total Simulasi</p>
            <p className="text-2xl font-bold text-blue-900">{simulationHistory.length}</p>
          </div>
          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4">
            <p className="text-xs text-slate-500">Total Percakapan</p>
            <p className="text-2xl font-bold text-indigo-900">{conversationHistory.length}</p>
          </div>
          <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4">
            <p className="text-xs text-slate-500">Status Dihubungi</p>
            <p className="text-2xl font-bold text-emerald-900">{statusStats.dihubungi}</p>
          </div>
          <div className="bg-red-50 border border-red-100 rounded-xl p-4">
            <p className="text-xs text-slate-500">Tidak Dihubungi</p>
            <p className="text-2xl font-bold text-red-900">{statusStats.tidakDihubungi}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
            <h2 className="font-bold text-slate-800 mb-3">Distribusi Topik</h2>
            <ul className="space-y-2 text-sm">
              <li className="flex justify-between"><span>Telecollection</span><span className="font-semibold">{topikStats.telecollection}</span></li>
              <li className="flex justify-between"><span>Retention</span><span className="font-semibold">{topikStats.retention}</span></li>
              <li className="flex justify-between"><span>Winback</span><span className="font-semibold">{topikStats.winback}</span></li>
            </ul>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
            <h2 className="font-bold text-slate-800 mb-3">Distribusi Risk Label</h2>
            {riskStats.length === 0 ? (
              <p className="text-sm text-slate-500">Belum ada data risiko.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {riskStats.slice(0, 6).map(([label, value]) => (
                  <li key={label} className="flex justify-between">
                    <span>{label}</span>
                    <span className="font-semibold">{value}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
