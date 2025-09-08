import React, { useState } from 'react';
import { UserCheck, Loader2, LogOut } from 'lucide-react';
import { useNavigate } from "react-router-dom";
import Alert from '../components/Alert';

// --- LOGIN PAGE COMPONENT ---
const LoginPage = ({ onLoginSuccess }: { onLoginSuccess: (customer_Id: string) => void }) => {
    const [customer_Id, setCustomer_Id] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [alert, setAlert] = useState<{ type: 'success' | 'error', title: string, message: string } | null>(null);
    const navigate = useNavigate();

        const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
        const token = sessionStorage.getItem('token');

        const handleCheckId = async (e: React.FormEvent) => {
            e.preventDefault();
            setLoading(true);
            setError('');
            setAlert(null);

            try {
                const res = await fetch(`${API_BASE_URL}/customer/check/${customer_Id}`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        ...(token ? { Authorization: `Bearer ${token}` } : {})
                    }
                });
                const data = await res.json();
                if (res.ok && data.valid) {
                    // Simpan customer_Id dan nama ke sessionStorage
                    sessionStorage.setItem('customer_id', customer_Id);
                    sessionStorage.setItem('customer_name', data.name || '');
                    onLoginSuccess(customer_Id);
                    navigate("/Dashboard");
                } else {
                    setAlert({ type: 'error', title: 'ID Tidak Valid', message: 'ID Pelanggan tidak ditemukan atau tidak valid.' });
                }
            } catch {
                setAlert({ type: 'error', title: 'Error', message: 'Gagal terhubung ke server.' });
            }
            setLoading(false);
        };

        const handleLogout = () => {
            sessionStorage.clear();
            navigate('/');
        };

    return (
        <div className="min-h-screen w-full bg-gray-100 flex flex-col items-center justify-center p-4 font-sans">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800">ICONNET AI Assistant</h1>
                    <p className="text-gray-500 mt-1">Silakan masukkan ID Pelanggan untuk memulai</p>
                </div>
                <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-200">
                    {/* Alert component */}
                    {alert && (
                      <Alert
                        type={alert.type}
                        title={alert.title}
                        message={alert.message}
                        onClose={() => setAlert(null)}
                      />
                    )}
                    <form onSubmit={handleCheckId} className="space-y-6">
                        <div>
                            <label htmlFor="customer-id" className="block text-sm font-medium text-gray-700 mb-2">
                                ID Pelanggan
                            </label>
                            <div className="relative">
                                <UserCheck className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    id="customer-id"
                                    type="text"
                                    value={customer_Id}
                                    onChange={(e) => setCustomer_Id(e.target.value)}
                                    placeholder="Contoh: ICON12345"
                                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                        </div>
                        {error && <p className="text-sm text-red-600">{error}</p>}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full px-6 py-3 rounded-lg font-semibold text-white flex items-center justify-center gap-3 transition-all duration-300 shadow-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="animate-spin h-5 w-5" />
                                    <span>Memeriksa...</span>
                                </>
                            ) : (
                                'Masuk Simulasi'
                            )}
                        </button>
                    </form>
                </div>
            </div>
                <div className="absolute top-6 right-8 z-10">
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl shadow transition-all"
                        title="Logout"
                    >
                        <LogOut className="w-5 h-5" />
                        <span className="hidden sm:inline">Logout</span>
                    </button>
                </div>
        </div>
    );
};

export default LoginPage;
