import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, User, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

// The admin secret is sent as an HTTP header (X-Admin-Key) to the backend.
// It must match ADMIN_SECRET_KEY in backend/.env.
// Default value mirrors the backend default: "tata-mitra-admin-2024"
// In production, set VITE_ADMIN_KEY env var (in frontend/.env) and
// ADMIN_SECRET_KEY env var (in backend/.env) to the same strong random secret.
const ADMIN_SECRET = import.meta.env.VITE_ADMIN_KEY ?? 'tata-mitra-admin-2024';

export const AdminLogin = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError]       = useState('');
    const [loading, setLoading]   = useState(false);
    const navigate                = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        // Step 1: client-side credential check (admin / admin123 for demo)
        if (username !== 'admin' || password !== 'admin123') {
            setError('Invalid credentials. Please try again.');
            setLoading(false);
            return;
        }

        // Step 2: verify the admin key works against the backend
        try {
            const res = await fetch('/admin/documents', {
                method: 'GET',
                headers: { 'X-Admin-Key': ADMIN_SECRET },
            });

            if (res.status === 403) {
                setError('Backend admin key mismatch. Check ADMIN_SECRET_KEY in backend/.env.');
                setLoading(false);
                return;
            }

            // Key is accepted — persist it for this session
            localStorage.setItem('isAdmin', 'true');
            localStorage.setItem('adminKey', ADMIN_SECRET);
            navigate('/admin/dashboard');
        } catch {
            setError('Cannot reach the backend server. Is it running?');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 to-indigo-900 flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white/10 backdrop-blur-xl p-8 rounded-3xl border border-white/20 w-full max-w-md shadow-2xl"
            >
                <div className="text-center mb-8">
                    <div className="mx-auto w-16 h-16 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full flex items-center justify-center mb-4 shadow-lg">
                        <Lock className="w-8 h-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-white">Employee Login</h2>
                    <p className="text-white/60 text-sm mt-2">Restricted Access Area</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-white/80 text-sm font-medium ml-1">Username</label>
                        <div className="relative">
                            <User className="absolute left-4 top-3.5 w-5 h-5 text-white/50" />
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-xl px-12 py-3 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                                placeholder="Enter username"
                                autoComplete="username"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-white/80 text-sm font-medium ml-1">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-4 top-3.5 w-5 h-5 text-white/50" />
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-xl px-12 py-3 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                                placeholder="Enter password"
                                autoComplete="current-password"
                            />
                        </div>
                    </div>

                    {error && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-xl p-3"
                        >
                            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                            <p className="text-red-400 text-sm">{error}</p>
                        </motion.div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold py-3.5 rounded-xl hover:shadow-lg hover:shadow-indigo-500/30 transition-all duration-200 active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <span className="flex gap-1">
                                <span className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:0ms]" />
                                <span className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:150ms]" />
                                <span className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:300ms]" />
                            </span>
                        ) : 'Access Dashboard'}
                    </button>
                </form>

                <p className="text-center text-white/25 text-xs mt-6">
                    Demo credentials: admin / admin123
                </p>
            </motion.div>
        </div>
    );
};
