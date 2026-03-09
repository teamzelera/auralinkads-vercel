/** @type {import('tailwindcss').Config} */
import logo from "../images/logo.jpeg";
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          bg: "#0B0F19",
          card: "#141A2A",
          border: "#1E2942",
        },
        accent: {
          purple: "#6C5CE7",
          "purple-hover": "#7D6FF0",
          cyan: "#00D1FF",
          "cyan-hover": "#00B8E0",
        },
        text: {
          primary: "#E6EAF2",
          secondary: "#9CA3AF",
          muted: "#6B7280",
        },
        status: {
          online: "#00D97E",
          offline: "#EF4444",
          idle: "#F59E0B",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 4px 24px rgba(0, 0, 0, 0.4)",
        glow: "0 0 20px rgba(108, 92, 231, 0.3)",
        "glow-cyan": "0 0 20px rgba(0, 209, 255, 0.3)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-in": "slideIn 0.3s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideIn: {
          "0%": { opacity: "0", transform: "translateX(-8px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
      },
    },
  },
  plugins: [],
};
