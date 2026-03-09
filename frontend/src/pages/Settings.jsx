import DashboardLayout from "../components/layout/DashboardLayout";
import { useAuth } from "../contexts/AuthContext";
import { Settings as SettingsIcon, User, Shield } from "lucide-react";

export default function Settings() {
    const { user } = useAuth();

    return (
        <DashboardLayout title="Settings">
            <div className="max-w-2xl space-y-6">
                {/* Profile */}
                <div className="card p-6">
                    <div className="flex items-center gap-3 mb-5">
                        <User className="w-5 h-5 text-accent-purple" />
                        <h2 className="font-semibold text-text-primary">Admin Profile</h2>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm text-text-secondary mb-1.5">Username</label>
                            <input className="input-field" value={user?.username || ""} readOnly />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1.5">Email</label>
                            <input className="input-field" value={user?.email || ""} readOnly />
                        </div>
                    </div>
                </div>

                {/* System Info */}
                <div className="card p-6">
                    <div className="flex items-center gap-3 mb-5">
                        <SettingsIcon className="w-5 h-5 text-accent-purple" />
                        <h2 className="font-semibold text-text-primary">System Configuration</h2>
                    </div>
                    <div className="space-y-3">
                        {[
                            { label: "Heartbeat Interval", value: "30 seconds" },
                            { label: "Offline Threshold", value: "90 seconds" },
                            { label: "Assignment Poll Interval", value: "60 seconds" },
                            { label: "Video Storage", value: "Cloudinary CDN" },
                            { label: "Real-time Protocol", value: "WebSocket (Django Channels)" },
                            { label: "Authentication", value: "JWT (Admin) / Device Tokens (Devices)" },
                        ].map(({ label, value }) => (
                            <div key={label} className="flex justify-between items-center py-2.5 border-b border-primary-border last:border-0">
                                <span className="text-text-secondary text-sm">{label}</span>
                                <span className="text-text-primary font-medium text-sm">{value}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Env reminder */}
                <div className="card p-4 border-accent-purple/30 bg-accent-purple/5">
                    <p className="text-sm text-text-secondary">
                        <span className="font-semibold text-accent-purple">Cloudinary Setup:</span> Add your Cloudinary credentials to{" "}
                        <code className="text-accent-cyan">backend/.env</code> to enable video uploads.
                    </p>
                </div>
            </div>
        </DashboardLayout>
    );
}
