import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Tv2, Eye, EyeOff, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import logo from "../images/logo.jpeg";

export default function Login() {
    const [form, setForm] = useState({ username: "", password: "" });
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await login(form.username, form.password);
            navigate("/");
        } catch (err) {
            toast.error(err.response?.data?.detail || "Invalid credentials");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-primary-bg flex items-center justify-center p-4">
            {/* Ambient glow */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-accent-purple/10 rounded-full blur-3xl" />
                <div className="absolute bottom-1/4 left-1/3 w-64 h-64 bg-accent-cyan/8 rounded-full blur-3xl" />
            </div>

            <div className="relative w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl shadow-glow mb-4 bg-white overflow-hidden">
                        <img src={logo} alt="AuraLink Logo" className="w-full h-full object-contain" />
                    </div>
                    <h1 className="text-3xl font-bold text-gradient mb-1">AuraLink</h1>
                    <p className="text-text-secondary">Digital Signage Management Platform</p>
                </div>

                {/* Form */}
                <div className="card p-8">
                    <h2 className="text-xl font-semibold text-text-primary mb-6">Admin Sign In</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-1.5">Username</label>
                            <input
                                id="username"
                                type="text"
                                placeholder="admin"
                                className="input-field"
                                value={form.username}
                                onChange={(e) => setForm({ ...form, username: e.target.value })}
                                required
                                autoComplete="username"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-1.5">Password</label>
                            <div className="relative">
                                <input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    className="input-field pr-10"
                                    value={form.password}
                                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                                    required
                                    autoComplete="current-password"
                                />
                                <button
                                    type="button"
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary transition-colors"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>
                        <button
                            id="login-btn"
                            type="submit"
                            disabled={loading}
                            className="btn-primary w-full py-3 flex items-center justify-center gap-2 mt-2"
                        >
                            {loading ? (
                                <><Loader2 className="w-4 h-4 animate-spin" />Signing in...</>
                            ) : "Sign In"}
                        </button>
                    </form>
                </div>

                <p className="text-center text-text-muted text-sm mt-6">
                    AuraLink v1.0 — Admin Portal
                </p>
            </div>
        </div>
    );
}
