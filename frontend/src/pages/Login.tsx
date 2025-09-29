import React, { useState } from 'react';
import { Mail, Lock, Loader2, Eye, EyeOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Alert from '../components/Alert';

// --- Auth Page Component ---
const AuthPage = ({ onLoginSuccess }: { onLoginSuccess: (user: { email: string; name: string }) => void }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [alert, setAlert] = useState<{ type: 'success' | 'error', title: string, message: string } | null>(null);
    const navigate = useNavigate();

    const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1/endpoints";
    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setAlert(null);
        try {
            const res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (res.ok && data.access_token) {
                // Simpan token JWT ke sessionStorage
                sessionStorage.setItem('token', data.access_token);
                sessionStorage.setItem('user_email', email); // Save user_email to sessionStorage
                onLoginSuccess({ email, name: data.name });
                navigate('/Home');
            } else {
                setAlert({ type: 'error', title: 'Login Gagal', message: data.message || 'Login gagal, silakan coba lagi.' });
            }
        } catch {
            setAlert({ type: 'error', title: 'Error', message: 'Gagal terhubung ke server.' });
        }
        setLoading(false);
    };

    return (
        <div
            className="min-h-screen w-full flex flex-col items-center justify-center p-4 font-sans"
            style={{
                backgroundImage: 'url(/bg_login.jpeg)',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat',
            }}
        >
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800">ICONNET AI Assistant</h1>
                    <p className="text-gray-500 mt-1">Masuk untuk memulai sesi simulasi</p>
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
                    <form onSubmit={handleLogin} className="space-y-6">
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                                Email
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="contoh@iconnet.com"
                                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                        </div>
                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                                Kata Sandi
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                                <button
                                    type="button"
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none"
                                    onClick={() => setShowPassword((prev) => !prev)}
                                    tabIndex={-1}
                                >
                                    {showPassword ? (
                                        <EyeOff className="h-5 w-5" />
                                    ) : (
                                        <Eye className="h-5 w-5" />
                                    )}
                                </button>
                            </div>
                        </div>
                        {error && <p className="text-sm text-red-600 text-center">{error}</p>}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full px-6 py-3 rounded-lg font-semibold text-white flex items-center justify-center gap-3 transition-all duration-300 shadow-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="animate-spin h-5 w-5" />
                                    <span>Memvalidasi...</span>
                                </>
                            ) : (
                                'Masuk'
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default AuthPage;
