import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import {
    LayoutDashboard, Monitor, Film, ListVideo,
    BarChart2, Settings, LogOut, Tv2, Zap
} from "lucide-react";
import logo from "../../images/logo.jpeg";

const navItems = [
    { to: "/", icon: LayoutDashboard, label: "Dashboard" },
    { to: "/devices", icon: Monitor, label: "Devices" },
    { to: "/videos", icon: Film, label: "Videos" },
    { to: "/playlists", icon: ListVideo, label: "Playlists" },
    { to: "/analytics", icon: BarChart2, label: "Analytics" },
    { to: "/settings", icon: Settings, label: "Settings" },
];

export default function Sidebar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <aside className="w-64 min-h-screen bg-primary-card border-r border-primary-border flex flex-col shrink-0">
            {/* Logo */}
            <div className="p-6 border-b border-primary-border">
                <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl flex items-center justify-center shadow-glow bg-white overflow-hidden">
                        <img src={logo} alt="AuraLink Logo" className="w-full h-full object-contain" />
                    </div>
                    <div>
                        <span className="font-bold text-lg text-gradient">AuraLink</span>
                        <p className="text-text-muted text-xs -mt-0.5">Signage Platform</p>
                    </div>
                </div>
            </div>

            {/* Nav */}
            <nav className="flex-1 p-4 space-y-1">
                {navItems.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        end={to === "/"}
                        className={({ isActive }) =>
                            isActive ? "sidebar-item-active" : "sidebar-item"
                        }
                    >
                        <Icon className="w-5 h-5 shrink-0" />
                        <span>{label}</span>
                    </NavLink>
                ))}
            </nav>

            {/* User */}
            <div className="p-4 border-t border-primary-border space-y-2">
                <div className="flex items-center gap-3 px-3 py-2">
                    <div className="w-8 h-8 rounded-full bg-accent-purple/20 border border-accent-purple/40 flex items-center justify-center">
                        <span className="text-accent-purple text-sm font-bold">
                            {user?.username?.[0]?.toUpperCase() || "A"}
                        </span>
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-text-primary truncate">{user?.username}</p>
                        <p className="text-xs text-text-muted truncate">{user?.email}</p>
                    </div>
                </div>
                <button onClick={handleLogout} className="sidebar-item w-full text-status-offline hover:text-status-offline hover:bg-status-offline/10">
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                </button>
            </div>
        </aside>
    );
}
