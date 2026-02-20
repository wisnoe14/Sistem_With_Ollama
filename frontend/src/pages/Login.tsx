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
        <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-blue-700 via-blue-600 to-blue-800 relative overflow-hidden">
            {/* Decorative elements */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
            <div className="absolute top-0 right-0 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
            <div className="absolute -bottom-8 left-20 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
            
            <div className="relative z-10 w-full max-w-md">
                <div className="absolute -top-12 left-1/2 -translate-x-1/2 z-20 w-24 h-24 rounded-full bg-blue-900 border-4 border-white/80 flex items-center justify-center shadow-lg">
                    <Mail className="w-9 h-9 text-white" />
                </div>
                <div className="relative z-10 bg-white/15 backdrop-blur-md border border-white/30 rounded-2xl shadow-2xl p-8 pt-16">
                    <div className="text-center mb-6">
                        <h2 className="text-2xl font-semibold text-white">Login</h2>
                        <p className="text-white/70 text-sm">Akses akun CS Anda</p>
                    </div>
                    
                    {/* Alert component */}
                    {alert && (
                        <div className="mb-4">
                            <Alert
                                type={alert.type}
                                title={alert.title}
                                message={alert.message}
                                onClose={() => setAlert(null)}
                            />
                        </div>
                    )}
                    <form onSubmit={handleLogin} className="space-y-4">
                        <div>
                            <label htmlFor="email" className="block text-xs font-semibold text-white/80 mb-2">
                                Email ID
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/70" />
                                <input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="name@iconnet.com"
                                    className="w-full bg-white/80 text-gray-800 placeholder-gray-500 pl-10 pr-4 py-2.5 rounded-md border border-white/40 focus:outline-none focus:ring-2 focus:ring-white/50"
                                    required
                                />
                            </div>
                        </div>
                        <div>
                            <label htmlFor="password" className="block text-xs font-semibold text-white/80 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/70" />
                                <input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full bg-white/80 text-gray-800 placeholder-gray-500 pl-10 pr-10 py-2.5 rounded-md border border-white/40 focus:outline-none focus:ring-2 focus:ring-white/50"
                                    required
                                />
                                <button
                                    type="button"
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                    onClick={() => setShowPassword((prev) => !prev)}
                                >
                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>
                        
                        <div className="flex items-center justify-between text-xs text-white/80">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="checkbox" className="w-3.5 h-3.5 rounded border-white/50 bg-white/20" />
                                <span>Remember me</span>
                            </label>
                            <a href="#" className="hover:text-white">Forgot Password?</a>
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full mt-2 bg-blue-900 hover:bg-blue-950 disabled:bg-gray-500 text-white font-semibold py-2.5 rounded-md transition-colors"
                        >
                            {loading ? (
                                <span className="inline-flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" />Loading</span>
                            ) : (
                                <span>LOGIN</span>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default AuthPage;
