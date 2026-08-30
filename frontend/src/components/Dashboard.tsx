import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { LogOut, LayoutDashboard, Users, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

interface DashboardStats {
    summary: {
        total: number;
        approved: number;
        rejected: number;
        conditional: number;
    };
    recent_events: Array<{
        timestamp: string;
        decision: string;
        risk_probability: number;
        eligibility_score: number;
    }>;
}

export const Dashboard = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        // Check auth
        const isAdmin = localStorage.getItem('isAdmin');
        if (!isAdmin) {
            navigate('/admin');
            return;
        }

        // Fetch stats
        const fetchStats = async () => {
            try {
                const res = await fetch('/api/dashboard/stats');
                const data = await res.json();
                setStats(data);
            } catch (err) {
                console.error('Failed to fetch dashboard stats', err);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('isAdmin');
        navigate('/admin');
    };

    if (loading || !stats) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
            </div>
        );
    }

    const pieData = [
        { name: 'Approved', value: stats.summary.approved },
        { name: 'Rejected', value: stats.summary.rejected },
        { name: 'Conditional', value: stats.summary.conditional },
    ];

    const COLORS = ['#10b981', '#ef4444', '#f59e0b'];

    const riskData = stats.recent_events.map((e, i) => ({
        name: `App ${i + 1}`,
        risk: (e.risk_probability * 100).toFixed(1),
        score: e.eligibility_score,
    })).slice(0, 20); // Show last 20 for cleaner chart

    return (
        <div className="min-h-screen bg-gray-900 text-white font-sans">
            {/* Sidebar / Nav */}
            <nav className="fixed top-0 w-full z-50 bg-gray-900/80 backdrop-blur-lg border-b border-gray-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-20">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-indigo-500 rounded-xl flex items-center justify-center">
                                <LayoutDashboard className="w-6 h-6 text-white" />
                            </div>
                            <span className="text-xl font-bold tracking-tight">OneBoard</span>
                        </div>
                        <Link
                            to="/admin/documents"
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-900/60 hover:bg-indigo-900/80 transition-colors text-sm font-medium border border-indigo-700/50 text-indigo-300"
                        >
                            📄 Documents
                        </Link>
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors text-sm font-medium border border-gray-700"
                        >
                            <LogOut className="w-4 h-4" />
                            Sign Out
                        </button>
                    </div>
                </div>
            </nav>

            <main className="pt-28 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
                <div className="mb-10">
                    <h1 className="text-4xl font-bold mb-2">Overview</h1>
                    <p className="text-gray-400">Real-time loan application analytics and performance metrics.</p>
                </div>

                {/* Info Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
                    <StatCard
                        title="Total Applications"
                        value={stats.summary.total}
                        icon={Users}
                        color="bg-indigo-500"
                    />
                    <StatCard
                        title="Approved"
                        value={stats.summary.approved}
                        icon={CheckCircle}
                        color="bg-emerald-500"
                    />
                    <StatCard
                        title="Rejected"
                        value={stats.summary.rejected}
                        icon={XCircle}
                        color="bg-red-500"
                    />
                    <StatCard
                        title="Conditional"
                        value={stats.summary.conditional}
                        icon={AlertTriangle}
                        color="bg-amber-500"
                    />
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-gray-800 rounded-3xl p-8 border border-gray-700 shadow-xl"
                    >
                        <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                            <span className="w-1 h-6 bg-indigo-500 rounded-full"></span>
                            Decision Distribution
                        </h3>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={80}
                                        outerRadius={120}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', borderRadius: '12px', color: '#fff' }}
                                        itemStyle={{ color: '#fff' }}
                                    />
                                    <Legend verticalAlign="bottom" height={36} iconType="circle" />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="bg-gray-800 rounded-3xl p-8 border border-gray-700 shadow-xl"
                    >
                        <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                            <span className="w-1 h-6 bg-pink-500 rounded-full"></span>
                            Recent Risk Profiles
                        </h3>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={riskData}>
                                    <XAxis dataKey="name" hide />
                                    <YAxis stroke="#4b5563" />
                                    <Tooltip
                                        cursor={{ fill: '#374151' }}
                                        contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', borderRadius: '12px', color: '#fff' }}
                                    />
                                    <Bar dataKey="risk" name="Risk %" fill="#8884d8" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="score" name="Score" fill="#ec4899" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </motion.div>
                </div>
            </main>
        </div>
    );
};

const StatCard = ({ title, value, icon: Icon, color }: any) => (
    <motion.div
        whileHover={{ y: -5 }}
        className="bg-gray-800 p-6 rounded-3xl border border-gray-700 shadow-lg"
    >
        <div className="flex items-center justify-between mb-4">
            <div className={`w-12 h-12 ${color} bg-opacity-20 rounded-2xl flex items-center justify-center`}>
                <Icon className={`w-6 h-6 ${color.replace('bg-', 'text-')}`} />
            </div>
            <span className="text-3xl font-bold">{value}</span>
        </div>
        <h4 className="text-gray-400 font-medium">{title}</h4>
    </motion.div>
);
