import { useState, useEffect, useRef } from "react";
import { Settings, X, LogOut, Trash2, Info, FileText, Mail } from "lucide-react";
import logo from "../images/logo.jpeg";

const PLAYER_API = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";
const HEARTBEAT_INTERVAL = 30000;
const POLL_INTERVAL = 60000;

export default function DevicePlayer() {
    const [step, setStep] = useState("login"); // "login" | "playing"
    const [code, setCode] = useState("");
    const [deviceToken, setDeviceToken] = useState(localStorage.getItem("device_token") || "");
    const [assignment, setAssignment] = useState(null);
    const [currentVideoIdx, setCurrentVideoIdx] = useState(0);
    const [error, setError] = useState("");
    const [showSettings, setShowSettings] = useState(false);
    const [settingsMenu, setSettingsMenu] = useState(null); // "main" | "about" | "terms" | "contact"
    const videoRef = useRef();
    const heartbeatRef = useRef();
    const pollRef = useRef();

    const deviceFetch = async (path, options = {}) => {
        return fetch(`${PLAYER_API}${path}`, {
            headers: { "Authorization": `Device ${deviceToken}`, "Content-Type": "application/json" },
            ...options,
        });
    };

    // On mount: if we have a token, go to playing
    useEffect(() => {
        if (deviceToken) setStep("playing");
    }, []);

    // Reset video tracking when active assignment changes 
    useEffect(() => {
        if (assignment?.id) setCurrentVideoIdx(0);
    }, [assignment?.id]);



    // Heartbeat
    useEffect(() => {
        if (step !== "playing") return;
        const sendHeartbeat = () =>
            deviceFetch("/devices/heartbeat/", {
                method: "POST",
                body: JSON.stringify({ status: "playing" }),
            }).catch(() => { });
        sendHeartbeat();
        heartbeatRef.current = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);
        return () => clearInterval(heartbeatRef.current);
    }, [step, deviceToken]);

    // Poll assignment
    useEffect(() => {
        if (step !== "playing") return;
        const pollAssignment = () =>
            deviceFetch("/device/get-playlist/")
                .then((r) => r.json())
                .then((data) => {
                    console.log("Device assignment fetched:", data);
                    if (data.error || data.assignment === null) setAssignment(null);
                    else setAssignment(data);
                })
                .catch((e) => console.error("Poll error:", e));
        pollAssignment();
        pollRef.current = setInterval(pollAssignment, POLL_INTERVAL);
        return () => clearInterval(pollRef.current);
    }, [step, deviceToken]);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");
        try {
            const res = await fetch(`${PLAYER_API}/devices/authenticate/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ device_code: code.toUpperCase() }),
            });
            const data = await res.json();
            if (!res.ok) { setError(data.error || "Authentication failed"); return; }
            localStorage.setItem("device_token", data.device_token);
            setDeviceToken(data.device_token);
            setStep("playing");
        } catch {
            setError("Network error. Check connection.");
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("device_token");
        setDeviceToken("");
        setAssignment(null);
        setStep("login");
        setCode("");
        setShowSettings(false);
    };

    const handleDeleteDevice = async () => {
        if (!confirm("Delete this device? This cannot be undone.")) return;
        handleLogout();
    };

    const isSingleVideo = !!assignment?.video;
    const videos = isSingleVideo
        ? [{ id: assignment.video.id, video: assignment.video }]
        : (assignment?.playlist?.videos || []);

    const onVideoEnded = () => {
        if (!assignment || videos.length === 0) return;

        // If there's only 1 video, it will loop naturally via the `loop` attribute.
        // We only need to manually advance if there are multiple videos.
        if (videos.length > 1) {
            const next = (currentVideoIdx + 1) % videos.length;
            if (next === 0 && !(assignment?.loop_enabled && (isSingleVideo || assignment?.playlist?.loop_enabled))) {
                console.log("Playlist finished, loop disabled.");
                return;
            }
            setCurrentVideoIdx(next);
        }
    };

    const currentVideo = videos.length > 0 ? videos[currentVideoIdx] : null;

    const autoplayEnabled = isSingleVideo ? true : (assignment?.playlist?.autoplay ?? true);
    const titleOverlay = isSingleVideo ? "" : (assignment?.playlist?.title_overlay || "");

    // Force explicit programmatic play whenever the video changes
    useEffect(() => {
        if (currentVideo && videoRef.current) {
            videoRef.current.load();
            videoRef.current.play().catch(e => console.warn("Autoplay naturally rejected by browser:", e));
        }
    }, [currentVideo?.id]);

    // Determine the next video to preload
    const nextVideoIdx = videos.length > 0 ? (currentVideoIdx + 1) % videos.length : null;
    const nextVideo = (nextVideoIdx !== null && (nextVideoIdx !== 0 || (assignment?.loop_enabled && (isSingleVideo || assignment?.playlist?.loop_enabled))))
        ? videos[nextVideoIdx]
        : null;

    // ── Login screen ──────────────────────────────────────
    if (step === "login") {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-center">
                    <div className="w-20 h-20 rounded-3xl mx-auto flex items-center justify-center mb-6 shadow-glow bg-white overflow-hidden">
                        <img src={logo} alt="AuraLink Logo" className="w-full h-full object-contain" />
                    </div>
                    <h1 className="text-2xl font-bold text-white mb-2">AuraLink Display</h1>
                    <p className="text-gray-500 mb-8 text-sm">Enter device code to activate</p>
                    <form onSubmit={handleLogin} className="space-y-4 w-72 mx-auto">
                        <input
                            className="w-full bg-gray-900 border border-gray-700 text-white text-center text-xl font-mono tracking-widest rounded-2xl px-4 py-4 outline-none focus:border-accent-purple"
                            placeholder="AUR-XXXX"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                            maxLength={8}
                            autoFocus
                        />
                        {error && <p className="text-red-400 text-sm">{error}</p>}
                        <button type="submit" className="w-full bg-gradient-primary text-white font-bold py-4 rounded-2xl shadow-glow">
                            Activate Screen
                        </button>
                    </form>
                </div>
            </div>
        );
    }

    // ── Player screen ──────────────────────────────────────
    return (
        <div className="min-h-screen bg-black relative overflow-hidden">
            {/* Video player */}
            {currentVideo?.video?.cloudinary_url ? (
                <>
                    <video
                        ref={videoRef}
                        key={currentVideo.id}
                        className="w-full h-screen object-cover"
                        src={currentVideo.video.cloudinary_url}
                        autoPlay={autoplayEnabled}
                        loop={videos.length === 1 && assignment?.loop_enabled && (isSingleVideo || assignment?.playlist?.loop_enabled)}
                        muted
                        playsInline
                        preload="auto"
                        onEnded={onVideoEnded}
                        onError={(e) => {
                            console.error("Video playback error details:", e);
                            onVideoEnded();
                        }}
                        style={{ transform: `rotate(${currentVideo.video.rotation || 0}deg)` }}
                    />

                    {/* Title Overlay */}
                    {titleOverlay && (
                        <div className="absolute bottom-10 left-10 right-10 pointer-events-none">
                            <h2 className="text-white text-5xl font-bold drop-shadow-lg tracking-tight bg-black/40 inline-block px-6 py-3 rounded-2xl backdrop-blur-sm shadow-xl border border-white/10">
                                {titleOverlay}
                            </h2>
                        </div>
                    )}
                    {/* Preload next video secretly for smooth transition */}
                    {nextVideo?.video?.cloudinary_url && (
                        <video
                            key={`preload-${nextVideo.id}`}
                            preload="auto"
                            className="hidden"
                            muted
                            playsInline
                            src={nextVideo.video.cloudinary_url}
                        />
                    )}
                </>
            ) : assignment ? (
                <div className="w-full h-screen flex flex-col items-center justify-center">
                    <p className="text-gray-600 text-lg">No playback media available for this device assignment.</p>
                </div>
            ) : (
                <div className="w-full h-screen flex flex-col items-center justify-center">
                    <div className="w-24 h-24 rounded-3xl flex items-center justify-center mb-6 shadow-glow animate-pulse-slow bg-white overflow-hidden">
                        <img src={logo} alt="AuraLink Logo" className="w-full h-full object-contain" />
                    </div>
                    <p className="text-gray-600 text-lg">Waiting for content...</p>
                </div>
            )}

            {/* Settings button */}
            <button
                onClick={() => { setShowSettings(true); setSettingsMenu("main"); }}
                className="absolute top-4 right-4 w-10 h-10 rounded-full bg-black/40 backdrop-blur-sm border border-white/10 flex items-center justify-center text-white/60 hover:text-white hover:bg-black/60 transition-all duration-200"
            >
                <Settings className="w-5 h-5" />
            </button>

            {/* Settings overlay */}
            {showSettings && (
                <div className="absolute inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-end">
                    <div className="w-72 h-full bg-gray-950 border-l border-gray-800 flex flex-col">
                        <div className="flex items-center justify-between p-5 border-b border-gray-800">
                            <span className="font-semibold text-white">
                                {settingsMenu === "main" ? "Settings" : settingsMenu === "about" ? "About" : settingsMenu === "terms" ? "Terms" : "Contact"}
                            </span>
                            <button onClick={() => { if (settingsMenu !== "main") setSettingsMenu("main"); else setShowSettings(false); }}>
                                <X className="w-5 h-5 text-gray-400" />
                            </button>
                        </div>

                        {settingsMenu === "main" && (
                            <div className="flex-1 p-4 space-y-2">
                                {[
                                    { icon: LogOut, label: "Logout", action: handleLogout, danger: true },
                                    { icon: Trash2, label: "Delete Device", action: handleDeleteDevice, danger: true },
                                    { icon: Info, label: "About", action: () => setSettingsMenu("about") },
                                    { icon: FileText, label: "Terms of Service", action: () => setSettingsMenu("terms") },
                                    { icon: Mail, label: "Contact", action: () => setSettingsMenu("contact") },
                                ].map(({ icon: Icon, label, action, danger }) => (
                                    <button key={label} onClick={action}
                                        className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl text-left transition-colors duration-200
                      ${danger ? "text-red-400 hover:bg-red-500/10" : "text-gray-300 hover:bg-gray-800"}`}>
                                        <Icon className="w-5 h-5" />
                                        <span className="font-medium">{label}</span>
                                    </button>
                                ))}
                            </div>
                        )}

                        {settingsMenu === "about" && (
                            <div className="flex-1 p-5 text-gray-400 text-sm space-y-3">
                                <p className="text-white font-semibold text-base">AuraLink Display v1.0</p>
                                <p>Digital Signage Management Platform — Device Player</p>
                                <p>This device is registered and managed by your organization's AuraLink admin.</p>
                            </div>
                        )}

                        {settingsMenu === "terms" && (
                            <div className="flex-1 p-5 text-gray-400 text-sm space-y-3 overflow-y-auto">
                                <p className="text-white font-semibold text-base">Terms of Service</p>
                                <p>This device is authorized for use as a display terminal within your organization.</p>
                                <p>Unauthorized use, modification, or access is prohibited.</p>
                            </div>
                        )}

                        {settingsMenu === "contact" && (
                            <div className="flex-1 p-5 text-gray-400 text-sm space-y-3">
                                <p className="text-white font-semibold text-base">Contact</p>
                                <p>For support, contact your AuraLink administrator.</p>
                                <p>AuraLink Digital Signage Platform</p>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
