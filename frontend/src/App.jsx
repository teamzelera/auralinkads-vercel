import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Devices from "./pages/Devices";
import Videos from "./pages/Videos";
import Playlists from "./pages/Playlists";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import DevicePlayer from "./pages/DevicePlayer";
import LocalVideoUpload from "./pages/LocalVideoUpload";
import FileTransfer from "./pages/FileTransfer";
import PhoneDashboard from "./pages/PhoneDashboard";
import LocalFileManager from "./pages/LocalFileManager";
import TransferHistory from "./pages/TransferHistory";
import DisplayRotation from "./pages/DisplayRotation";
import logo from "./images/logo.jpeg";
import React from "react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    this.setState({ errorInfo });
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 20, background: "black", color: "red", minHeight: "100vh" }}>
          <h1 style={{ fontSize: 24, fontWeight: "bold" }}>Application Error</h1>
          <p>{this.state.error && this.state.error.toString()}</p>
          <pre style={{ marginTop: 20, fontSize: 12, color: "orange", whiteSpace: "pre-wrap" }}>
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen bg-primary-bg flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl mx-auto flex items-center justify-center animate-pulse bg-white overflow-hidden">
            <img src={logo} alt="AuraLink Logo" className="w-full h-full object-contain" />
          </div>
          <p className="text-text-muted text-sm">Loading...</p>
        </div>
      </div>
    );
  }
  return user ? children : <Navigate to="/ladminsirlogin" replace />;
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: "#141A2A",
                color: "#E6EAF2",
                border: "1px solid #1E2942",
                borderRadius: "12px",
              },
              success: { iconTheme: { primary: "#00D97E", secondary: "#141A2A" } },
              error: { iconTheme: { primary: "#EF4444", secondary: "#141A2A" } },
            }}
          />
          <Routes>
            <Route path="/ladminsirlogin" element={<Login />} />
            <Route path="/login" element={<Navigate to="/ladminsirlogin" replace />} />
            
            <Route path="/" element={<DevicePlayer />} />
            <Route path="/device" element={<DevicePlayer />} />
            
            <Route path="/device/local-video" element={<LocalVideoUpload />} />
            <Route path="/device/transfer" element={<FileTransfer />} />
            <Route path="/device/phone" element={<PhoneDashboard />} />
            <Route path="/device/files" element={<LocalFileManager />} />
            <Route path="/device/transfers" element={<TransferHistory />} />
            <Route path="/device/display-rotation" element={<DisplayRotation />} />
            
            <Route
              path="/dashboard"
              element={<PrivateRoute><Dashboard /></PrivateRoute>}
            />
            <Route
              path="/devices"
              element={<PrivateRoute><Devices /></PrivateRoute>}
            />
            <Route
              path="/videos"
              element={<PrivateRoute><Videos /></PrivateRoute>}
            />
            <Route
              path="/playlists"
              element={<PrivateRoute><Playlists /></PrivateRoute>}
            />
            <Route
              path="/analytics"
              element={<PrivateRoute><Analytics /></PrivateRoute>}
            />
            <Route
              path="/settings"
              element={<PrivateRoute><Settings /></PrivateRoute>}
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}
