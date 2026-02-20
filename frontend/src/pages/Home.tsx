import React, { useState, useEffect } from 'react';
import { UserCheck, Loader2, LogOut, MessageCircle, BarChart3, BookOpen, Users, CheckCircle, History } from 'lucide-react';
import { useNavigate } from "react-router-dom";
import Alert from '../components/Alert';

// --- LOGIN PAGE COMPONENT ---
const LoginPage = ({ onLoginSuccess }: { onLoginSuccess: (customer_Id: string) => void }) => {
    const [customer_Id, setCustomer_Id] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [alert, setAlert] = useState<{ type: 'success' | 'error', title: string, message: string } | null>(null);
    const [isLoggedIn, setIsLoggedIn] = useState(!!sessionStorage.getItem('customer_id'));
    const [showAllCustomers, setShowAllCustomers] = useState(false);
    const [customers, setCustomers] = useState<Array<{ customer_id: string; name: string }>>([]);
    const [loadingCustomers, setLoadingCustomers] = useState(false);
    const [contactedCustomers, setContactedCustomers] = useState<Array<{ customer_id: string; name: string; status_dihubungi: boolean; last_contact?: string }>>([]);
    const [loadingContacted, setLoadingContacted] = useState(false);
    const navigate = useNavigate();

    const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1/endpoints";
    const token = sessionStorage.getItem('token');
    const hasToken = !!token;

    // Fetch customer list dari backend
    useEffect(() => {
        const fetchCustomers = async () => {
            setLoadingCustomers(true);
            try {
                const res = await fetch(`${API_BASE_URL}/customer/list`, {
                    headers: {
                        "Content-Type": "application/json",
                        ...(token ? { Authorization: `Bearer ${token}` } : {})
                    }
                });
                const data = await res.json();
                if (res.ok && data.customers) {
                    setCustomers(data.customers);
                }
            } catch (error) {
                console.error('Error fetching customers:', error);
            }
            setLoadingCustomers(false);
        };
        fetchCustomers();
    }, [token]);

    // Fetch contacted customers (pelanggan yang sudah dihubungi)
    useEffect(() => {
        const fetchContactedCustomers = async () => {
            setLoadingContacted(true);
            try {
                const res = await fetch(`${API_BASE_URL}/customer/list`, {
                    headers: {
                        "Content-Type": "application/json",
                        ...(token ? { Authorization: `Bearer ${token}` } : {})
                    }
                });
                const data = await res.json();
                if (res.ok && data.customers) {
                    // Filter only contacted customers
                    const contacted = data.customers.filter((c: any) => c.status_dihubungi === true);
                    setContactedCustomers(contacted);
                }
            } catch (error) {
                console.error('Error fetching contacted customers:', error);
            }
            setLoadingContacted(false);
        };
        fetchContactedCustomers();
        // Refresh every 30 seconds
        const interval = setInterval(fetchContactedCustomers, 30000);
        return () => clearInterval(interval);
    }, [token]);

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
                setIsLoggedIn(true);
                onLoginSuccess(customer_Id);
                // Langsung navigate ke halaman chat
                navigate('/chat');
            } else {
                setAlert({ type: 'error', title: 'ID Tidak Valid', message: 'ID Pelanggan tidak ditemukan atau tidak valid.' });
            }
        } catch {
            setAlert({ type: 'error', title: 'Error', message: 'Gagal terhubung ke server.' });
        }
        setLoading(false);
    };

    // Fungsi untuk logout total (keluar aplikasi)
    const handleLogout = () => {
        sessionStorage.clear();
        setIsLoggedIn(false);
        navigate('/');
    };

    // Fungsi untuk ganti ID saja (reset session dan form, tanpa redirect)
    const handleChangeId = () => {
        sessionStorage.removeItem('customer_id');
        sessionStorage.removeItem('customer_name');
        setCustomer_Id('');
        setIsLoggedIn(false);
    };

    // Single unified page - always visible
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 relative overflow-hidden" style={{ fontFamily: "'Inter', 'Poppins', sans-serif" }}>
            {/* Animated Background Elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -left-40 w-80 h-80 bg-blue-500/10 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob"></div>
                <div className="absolute -top-40 right-0 w-80 h-80 bg-cyan-500/10 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob animation-delay-2000"></div>
                <div className="absolute bottom-0 left-20 w-80 h-80 bg-indigo-500/10 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob animation-delay-4000"></div>
                <div className="absolute -bottom-32 right-20 w-96 h-96 bg-blue-600/5 rounded-full mix-blend-screen filter blur-3xl opacity-50"></div>
            </div>

            {/* Content Wrapper */}
            <div className="relative z-10">
                {/* Top Navigation Bar */}
                {hasToken && (
                    <nav className="bg-white/5 backdrop-blur-xl border-b border-white/10 shadow-lg sticky top-0 z-50">
                        <div className="max-w-7xl mx-auto px-8 py-5">
                            <div className="flex items-center justify-between">
                                {/* Logo Section */}
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-blue-600 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
                                        <MessageCircle className="w-7 h-7 text-white" />
                                    </div>
                                    <div>
                                        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-300 to-cyan-300 bg-clip-text text-transparent">ICONNET AI Assistant</h1>
                                        <p className="text-xs text-blue-300/70">Enterprise Customer Service Platform</p>
                                    </div>
                                </div>

                                {/* Navigation Menu */}
                                <div className="hidden lg:flex items-center gap-1">
                                    <button
                                        onClick={() => navigate('/customer-list')}
                                        className="flex items-center gap-2 px-5 py-2.5 text-blue-200 hover:text-blue-100 hover:bg-blue-500/20 rounded-lg transition-all duration-200 cursor-pointer"
                                        type="button"
                                    >
                                        <Users className="w-4 h-4" />
                                        <span className="text-sm font-medium">Daftar Pelanggan</span>
                                    </button>
                                    <button
                                        onClick={() => navigate('/analytics')}
                                        className="flex items-center gap-2 px-5 py-2.5 text-blue-200 hover:text-blue-100 hover:bg-blue-500/20 rounded-lg transition-all duration-200 cursor-pointer"
                                        type="button"
                                    >
                                        <BarChart3 className="w-4 h-4" />
                                        <span className="text-sm font-medium">Analytics</span>
                                    </button>
                                    <button
                                        onClick={() => navigate('/knowledge-base')}
                                        className="flex items-center gap-2 px-5 py-2.5 text-blue-200 hover:text-blue-100 hover:bg-blue-500/20 rounded-lg transition-all duration-200 cursor-pointer"
                                        type="button"
                                    >
                                        <BookOpen className="w-4 h-4" />
                                        <span className="text-sm font-medium">Knowledge Base</span>
                                    </button>
                                    <button
                                        onClick={() => navigate('/customer-management')}
                                        className="flex items-center gap-2 px-5 py-2.5 text-blue-200 hover:text-blue-100 hover:bg-blue-500/20 rounded-lg transition-all duration-200 cursor-pointer"
                                        type="button"
                                    >
                                        <Users className="w-4 h-4" />
                                        <span className="text-sm font-medium">Customers</span>
                                    </button>
                                    <button
                                        onClick={() => navigate('/riwayat-percakapan')}
                                        className="flex items-center gap-2 px-5 py-2.5 text-blue-200 hover:text-blue-100 hover:bg-blue-500/20 rounded-lg transition-all duration-200 cursor-pointer"
                                        type="button"
                                    >
                                        <History className="w-4 h-4" />
                                        <span className="text-sm font-medium">Riwayat</span>
                                    </button>
                                    <button
                                        onClick={() => navigate('/customer-actions')}
                                        className="flex items-center gap-2 px-5 py-2.5 text-blue-200 hover:text-blue-100 hover:bg-blue-500/20 rounded-lg transition-all duration-200 cursor-pointer"
                                        type="button"
                                    >
                                        <CheckCircle className="w-4 h-4" />
                                        <span className="text-sm font-medium">Daftar Tindakan</span>
                                    </button>
                                </div>

                                {/* Logout Button */}
                                <button
                                    onClick={handleLogout}
                                    className="flex items-center gap-2 px-5 py-2.5 bg-red-600/90 hover:bg-red-700 text-white text-sm font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
                                >
                                    <LogOut className="w-4 h-4" />
                                    <span className="hidden sm:inline">Logout</span>
                                </button>
                            </div>
                        </div>
                    </nav>
                )}

                {/* Main Content Area */}
                <div className={`${hasToken ? 'py-12' : 'py-20 min-h-screen flex items-center justify-center'}`}>
                    <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8">
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            {/* Main Content - Input Customer */}
                            <div className="lg:col-span-2">
                                {/* Header Section */}
                                {!hasToken && (
                                    <div className="text-center mb-12 space-y-3">
                                        <h1 className="text-4xl sm:text-5xl font-extrabold bg-gradient-to-r from-blue-300 via-blue-400 to-cyan-300 bg-clip-text text-transparent">
                                            ICONNET AI Assistant
                                        </h1>
                                        <p className="text-lg text-blue-200/80">Intelligent Customer Service Platform</p>
                                        <div className="flex justify-center gap-2 pt-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                                            <div className="w-1.5 h-1.5 rounded-full bg-cyan-500"></div>
                                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                                        </div>
                                    </div>
                                )}

                                {/* Customer Active Badge */}
                                {isLoggedIn && (
                                    <div className="flex justify-center mb-8">
                                        <div className="inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/40 rounded-full backdrop-blur-sm">
                                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                                            <span className="text-sm font-semibold text-green-300">
                                                Customer Active: <span className="font-bold">{sessionStorage.getItem('customer_id')}</span>
                                            </span>
                                        </div>
                                    </div>
                                )}

                                {/* Validation Card */}
                                <div className="bg-gradient-to-br from-white to-blue-50/50 rounded-3xl shadow-2xl border border-gray-100 overflow-hidden backdrop-blur-sm">
                                    {/* Card Header */}
                                    <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 px-8 sm:px-10 py-8 relative overflow-hidden">
                                        {/* Header Background Effect */}
                                        <div className="absolute inset-0 opacity-10">
                                            <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full filter blur-2xl"></div>
                                        </div>

                                        <div className="flex items-center gap-4 relative z-10">
                                            <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center shadow-xl backdrop-blur-sm">
                                                <UserCheck className="w-8 h-8 text-white" />
                                            </div>
                                            <div>
                                                <h2 className="text-3xl font-bold text-white">Verifikasi Pelanggan</h2>
                                                <p className="text-blue-100 text-sm mt-1">Pilih pelanggan untuk memulai sesi percakapan</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Card Body */}
                                    <div className="p-8 sm:p-10 space-y-7">
                                        {/* Alert Notification */}
                                        {alert && (
                                            <div className="mb-4 animate-in fade-in slide-in-from-top">
                                                <Alert
                                                    type={alert.type}
                                                    title={alert.title}
                                                    message={alert.message}
                                                    onClose={() => setAlert(null)}
                                                />
                                            </div>
                                        )}

                                        <div className="space-y-6">
                                            <div className="p-4 bg-white border-2 border-gray-200 rounded-xl shadow-sm">
                                                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Pelanggan Terpilih</p>
                                                <p className="mt-1 text-base font-bold text-gray-900">
                                                    {customers.find(customer => customer.customer_id === customer_Id)
                                                        ? `${customer_Id} • ${customers.find(customer => customer.customer_id === customer_Id)?.name || '-'}`
                                                        : 'Belum dipilih'}
                                                </p>
                                            </div>

                                            <div className="space-y-3">
                                                <button
                                                    type="button"
                                                    disabled={loading || !customers.find(customer => customer.customer_id === customer_Id)}
                                                    onClick={() => {
                                                        const selectedCustomer = customers.find(customer => customer.customer_id === customer_Id);
                                                        if (!selectedCustomer) {
                                                            setAlert({ type: 'error', title: 'Belum Dipilih', message: 'Silakan pilih pelanggan dari daftar di samping.' });
                                                            return;
                                                        }
                                                        sessionStorage.setItem('customer_id', selectedCustomer.customer_id);
                                                        sessionStorage.setItem('customer_name', selectedCustomer.name || '');
                                                        setIsLoggedIn(true);
                                                        onLoginSuccess(selectedCustomer.customer_id);
                                                        navigate('/chat');
                                                    }}
                                                    className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white text-lg font-bold rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-0.5 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-3 active:scale-95"
                                                >
                                                    <CheckCircle className="w-5 h-5" />
                                                    <span>Mulai Percakapan</span>
                                                </button>

                                                <button
                                                    type="button"
                                                    onClick={handleChangeId}
                                                    className="w-full px-6 py-3 bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white text-sm font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 active:scale-95"
                                                >
                                                    Ganti Pilihan
                                                </button>
                                            </div>
                                        </div>

                                        {/* Info Box */}
                                        <div className="p-5 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-xl">
                                            <div className="flex items-start gap-3">
                                                <div className="w-5 h-5 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                                                    <span className="text-white text-xs font-bold">i</span>
                                                </div>
                                                <p className="text-sm text-blue-900 font-medium">
                                                    Pilih pelanggan dari daftar di samping untuk memulai percakapan
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Quick Actions - Daftar Tindakan */}
                                {hasToken && (
                                    <div className="mt-8">
                                        <div className="bg-gradient-to-br from-white to-purple-50/50 rounded-3xl shadow-2xl border border-gray-100 overflow-hidden backdrop-blur-sm">
                                            <div className="bg-gradient-to-r from-purple-600 via-purple-700 to-indigo-700 px-8 py-6">
                                                <div className="flex items-center gap-4">
                                                    <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center shadow-xl backdrop-blur-sm">
                                                        <CheckCircle className="w-8 h-8 text-white" />
                                                    </div>
                                                    <div>
                                                        <h3 className="text-2xl font-bold text-white">Daftar Tindakan</h3>
                                                        <p className="text-purple-100 text-sm mt-1">Monitor customer yang perlu follow-up</p>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="p-8">
                                                <p className="text-gray-700 mb-6">
                                                    Pelanggan yang memerlukan tindakan lanjutan
                                                </p>
                                                
                                                {/* List Customer Actions */}
                                                <div className="space-y-3 mb-6 max-h-[400px] overflow-y-auto">
                                                    {(() => {
                                                        const history = JSON.parse(localStorage.getItem('conversationHistory') || '[]');
                                                        const actionableCustomers = history.filter((item: any) => 
                                                            item.customer_id && item.customer_id !== '-' && item.topik
                                                        ).slice(0, 5); // Show last 5

                                                        if (actionableCustomers.length === 0) {
                                                            return (
                                                                <div className="text-center py-8 text-gray-500">
                                                                    <p className="text-sm">Belum ada customer yang perlu tindakan</p>
                                                                </div>
                                                            );
                                                        }

                                                        return actionableCustomers.map((item: any, index: number) => (
                                                            <div key={index} className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-100 hover:shadow-md transition-shadow">
                                                                <div className="flex items-start justify-between mb-2">
                                                                    <div className="flex items-center gap-2">
                                                                        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg flex items-center justify-center">
                                                                            <Users className="w-4 h-4 text-white" />
                                                                        </div>
                                                                        <div>
                                                                            <p className="font-bold text-gray-900 text-sm">{item.customer_id}</p>
                                                                            <p className="text-xs text-gray-600">{item.customer_name || '-'}</p>
                                                                        </div>
                                                                    </div>
                                                                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                                                        item.topik === 'telecollection' ? 'bg-orange-100 text-orange-700' :
                                                                        item.topik === 'retention' ? 'bg-green-100 text-green-700' :
                                                                        'bg-purple-100 text-purple-700'
                                                                    }`}>
                                                                        {item.topik}
                                                                    </span>
                                                                </div>
                                                                <div className="space-y-1 mt-3">
                                                                    <div className="flex items-center gap-2 text-xs">
                                                                        <span className="text-gray-500">Status:</span>
                                                                        <span className="font-medium text-gray-700">{item.status_dihubungi || item.status || '-'}</span>
                                                                    </div>
                                                                    {item.alasan && item.alasan !== '-' && (
                                                                        <div className="flex items-start gap-2 text-xs">
                                                                            <span className="text-gray-500 whitespace-nowrap">Alasan:</span>
                                                                            <span className="font-medium text-gray-700 line-clamp-2">{item.alasan}</span>
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        ));
                                                    })()}
                                                </div>

                                                {/* Action Buttons */}
                                                <div className="grid grid-cols-2 gap-3">
                                                    <button
                                                        onClick={() => navigate('/admin-input-customer')}
                                                        className="px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-700 hover:from-green-700 hover:to-emerald-800 text-white font-bold rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-0.5 flex items-center justify-center gap-2 active:scale-95"
                                                    >
                                                        <UserCheck className="w-5 h-5" />
                                                        <span>Input Customer</span>
                                                    </button>
                                                    <button
                                                        onClick={() => navigate('/customer-actions')}
                                                        className="px-6 py-4 bg-gradient-to-r from-purple-600 to-indigo-700 hover:from-purple-700 hover:to-indigo-800 text-white font-bold rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-0.5 flex items-center justify-center gap-2 active:scale-95"
                                                    >
                                                        <CheckCircle className="w-5 h-5" />
                                                        <span>Lihat Semua</span>
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Footer Note */}
                                {!hasToken && (
                                    <div className="mt-12 text-center space-y-2">
                                        <p className="text-blue-300/70 text-sm">Powered by ICONNET AI • Customer Service Excellence</p>
                                        <div className="flex justify-center gap-4 mt-6 text-xs text-blue-300/50">
                                            <span>Secure • Reliable • Enterprise-Grade</span>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Sidebar */}
                            <div className="lg:col-span-1 space-y-6">
                                {hasToken && (
                                    <div className="bg-gradient-to-br from-white to-blue-50/50 rounded-3xl shadow-2xl border border-gray-100 overflow-hidden backdrop-blur-sm sticky top-24">
                                        {/* Sidebar Header */}
                                        <div className="bg-gradient-to-r from-purple-600 via-purple-700 to-indigo-700 px-6 py-5">
                                            <div className="flex items-center justify-between mb-3">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                                                        <History className="w-5 h-5 text-white" />
                                                    </div>
                                                    <div>
                                                        <h3 className="text-lg font-bold text-white">{showAllCustomers ? 'Semua Pelanggan' : 'Riwayat Hari Ini'}</h3>
                                                        <p className="text-xs text-purple-200">Customer yang sudah dihubungi</p>
                                                    </div>
                                                </div>
                                            </div>
                                            {/* Toggle Filter */}
                                            <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-lg p-1">
                                                <button
                                                    onClick={() => setShowAllCustomers(false)}
                                                    className={`flex-1 px-3 py-2 text-xs font-semibold rounded-md transition-all duration-200 ${
                                                        !showAllCustomers 
                                                            ? 'bg-white text-purple-700 shadow-lg' 
                                                            : 'text-white/70 hover:text-white'
                                                    }`}
                                                >
                                                    Hari Ini
                                                </button>
                                                <button
                                                    onClick={() => setShowAllCustomers(true)}
                                                    className={`flex-1 px-3 py-2 text-xs font-semibold rounded-md transition-all duration-200 ${
                                                        showAllCustomers 
                                                            ? 'bg-white text-purple-700 shadow-lg' 
                                                            : 'text-white/70 hover:text-white'
                                                    }`}
                                                >
                                                    Semua
                                                </button>
                                            </div>
                                        </div>

                                        {/* Sidebar Body */}
                                        <div className="p-5 max-h-[600px] overflow-y-auto">
                                            {(() => {
                                                const history = JSON.parse(localStorage.getItem('conversationHistory') || '[]');
                                                const today = new Date().toLocaleDateString('id-ID');
                                                
                                                // Deduplikasi berdasarkan customer_id
                                                const uniqueCustomers = new Map();
                                                history.forEach((item: any) => {
                                                    if (!uniqueCustomers.has(item.customer_id) || 
                                                        new Date(item.tanggal) > new Date(uniqueCustomers.get(item.customer_id).tanggal)) {
                                                        uniqueCustomers.set(item.customer_id, item);
                                                    }
                                                });
                                                const allCustomers = Array.from(uniqueCustomers.values());
                                                
                                                const todayHistory = showAllCustomers 
                                                    ? allCustomers 
                                                    : allCustomers.filter((item: any) => {
                                                        const itemDate = item.tanggal?.split(',')[0];
                                                        return itemDate === today;
                                                    });

                                                if (todayHistory.length === 0) {
                                                    return (
                                                        <div className="text-center py-12">
                                                            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                                                <History className="w-8 h-8 text-gray-400" />
                                                            </div>
                                                            <p className="text-gray-500 text-sm">
                                                                {showAllCustomers 
                                                                    ? 'Belum ada customer\nyang pernah dihubungi' 
                                                                    : 'Belum ada customer\nyang dihubungi hari ini'
                                                                }
                                                            </p>
                                                        </div>
                                                    );
                                                }

                                                return (
                                                    <div className="space-y-3">
                                                        {todayHistory.map((item: any, index: number) => (
                                                            <div key={index} className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-all duration-200 hover:border-blue-300">
                                                                <div className="flex items-start justify-between mb-2">
                                                                    <div className="flex items-center gap-2">
                                                                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                                                            <UserCheck className="w-4 h-4 text-blue-600" />
                                                                        </div>
                                                                        <div>
                                                                            <p className="text-sm font-bold text-gray-900">{item.customer_id || '-'}</p>
                                                                            <p className="text-xs text-gray-500">{item.nama || '-'}</p>
                                                                        </div>
                                                                    </div>
                                                                    {item.status && (
                                                                        <span className={`text-[10px] font-semibold px-2 py-1 rounded-full ${item.status.includes('BERHASIL') ? 'bg-green-100 text-green-700' :
                                                                                item.status.includes('AKAN') ? 'bg-blue-100 text-blue-700' :
                                                                                    item.status.includes('SUDAH') ? 'bg-green-100 text-green-700' :
                                                                                        'bg-gray-100 text-gray-700'
                                                                            }`}>
                                                                            {item.status}
                                                                        </span>
                                                                    )}
                                                                </div>
                                                                <div className="flex items-center gap-2 text-xs text-gray-500">
                                                                    <span className="px-2 py-1 bg-purple-50 text-purple-600 rounded-md font-medium">
                                                                        {item.topik || '-'}
                                                                    </span>
                                                                    <span>•</span>
                                                                    <span>{item.tanggal?.split(',')[1]?.trim() || '-'}</span>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                );
                                            })()}
                                        </div>

                                        {/* Sidebar Footer */}
                                        <div className="border-t border-gray-200 px-5 py-3 bg-gray-50">
                                            <button
                                                onClick={() => navigate('/riwayat-percakapan')}
                                                className="w-full text-xs text-blue-600 hover:text-blue-700 font-semibold flex items-center justify-center gap-1 py-2"
                                            >
                                                <span>Lihat Semua Riwayat</span>
                                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                )}

                                <div className="bg-gradient-to-br from-white to-blue-50/50 rounded-3xl shadow-2xl border border-gray-100 overflow-hidden backdrop-blur-sm">
                                    <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 px-6 py-5">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center shadow-lg">
                                                <Users className="w-5 h-5 text-white" />
                                            </div>
                                            <div>
                                                <h3 className="text-lg font-bold text-white">Daftar Pelanggan</h3>
                                                <p className="text-xs text-blue-100">Pilih pelanggan untuk isi otomatis</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="p-5">
                                        <div className="space-y-3">
                                            <label className="block text-sm font-bold text-gray-700">
                                                Atau Pilih dari Daftar
                                            </label>
                                            <div className="bg-white border-2 border-gray-200 rounded-xl shadow-md max-h-[360px] overflow-y-auto">
                                                {loadingCustomers ? (
                                                    <div className="p-6 flex items-center justify-center">
                                                        <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                                                        <span className="ml-3 text-sm text-gray-600">Memuat...</span>
                                                    </div>
                                                ) : customers.length > 0 ? (
                                                    <>
                                                        <div className="p-3 bg-gradient-to-r from-blue-50 to-cyan-50 border-b border-gray-200 sticky top-0">
                                                            <p className="text-xs font-bold text-blue-900 flex items-center gap-2">
                                                                <Users className="w-4 h-4" />
                                                                Daftar Pelanggan ({customers.length})
                                                            </p>
                                                        </div>
                                                        <div className="divide-y divide-gray-100">
                                                            {customers
                                                                .filter(customer => 
                                                                    customer_Id === '' || 
                                                                    customer.customer_id.toLowerCase().includes(customer_Id.toLowerCase()) ||
                                                                    customer.name.toLowerCase().includes(customer_Id.toLowerCase())
                                                                )
                                                                .map((customer, index) => (
                                                                    <button
                                                                        key={index}
                                                                        type="button"
                                                                        onClick={() => {
                                                                            setCustomer_Id(customer.customer_id);
                                                                        }}
                                                                        className="w-full px-4 py-3 text-left hover:bg-blue-50 transition-colors duration-150 flex items-center gap-3 group"
                                                                    >
                                                                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-200">
                                                                            <UserCheck className="w-5 h-5 text-white" />
                                                                        </div>
                                                                        <div className="flex-1 min-w-0">
                                                                            <p className="text-sm font-bold text-gray-900 group-hover:text-blue-700">{customer.customer_id}</p>
                                                                            <p className="text-xs text-gray-600 truncate">{customer.name}</p>
                                                                        </div>
                                                                        <div className="text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                                            </svg>
                                                                        </div>
                                                                    </button>
                                                                ))
                                                            }
                                                        </div>
                                                    </>
                                                ) : (
                                                    <div className="p-6 text-center text-sm text-gray-500">
                                                        Tidak ada data pelanggan
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
