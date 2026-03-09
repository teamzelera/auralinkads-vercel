<div align="center">
  <h1>🌟 AuraLink</h1>
  <p><strong>AuraLink is a Modern Digital Signage Management Platform</strong></p>
  <p><i>My first full-stack application built with React & Django!</i></p>

  <p>
    <a href="https://auralinkads.in" target="_blank">
      <img src="https://img.shields.io/badge/Domain-auralinkads.in-blue?style=for-the-badge&logo=google-chrome" alt="Website" />
    </a>
    <img src="https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
    <img src="https://img.shields.io/badge/Backend-Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
    <img src="https://img.shields.io/badge/Database-PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  </p>
</div>

---

## 🚀 About the Project

**AuraLink** is a digital signage management platform designed to control and monitor media playback across multiple screens. This is my **first full-stack application** ever built! It features a robust administration dashboard to manage devices, video playlists, and schedules remotely.

- **Domain**: [https://auralinkads.in](https://auralinkads.in)
- **Frontend Hosting**: Vercel 🚀
- **Backend Hosting**: Render 🌩️

---

## ✨ Features

- **Device Management**: Generate unique device codes to easily register and authenticate screens.
- **Content Provisioning**: Upload videos seamlessly (stored securely on Cloudinary) and organize them into powerful playlists.
- **Real-Time Monitoring**: Live device heartbeat polling via sophisticated WebSocket (Django Channels) integration. Ensure your screens are online and playing correctly.
- **Scheduling System**: Schedule when specific playlists run on assigned devices automatically. 
- **Offline / Idle Handling**: Intelligent playback logic ensures your screens show branding or fallbacks when idle or disconnected.

---

## 🛠️ Technology Stack

### Frontend (React Dashboard & Player)
- **React.js**: For dynamic, component-based UIs on the Admin Panel and the Screen Player.
- **Hosting**: Deployed seamlessly on **Vercel**.

### Backend (Django REST Framework)
- **Django & DRF**: Provides robust, scalable REST APIs.
- **Django Channels**: Real-time websocket communication.
- **JWT Authentication**: Secure API access with JSON Web Tokens.
- **Hosting**: Deployed reliably on **Render**.

### Storage & Database
- **PostgreSQL**: Primary relational database.
- **Cloudinary**: Optimal video and thumbnail storage and delivery.

---

## 🧑‍💻 Architecture Highlights

- **A.N.T. 3-Layer Architecture**: Streamlined SOPs, Django URL gating, and atomic Python utilities.
- **Dual Authentication Model**: 
  - Standard User/Password + JWT for the Admin Panel.
  - Specific opaque Device Tokens generated dynamically for displays.
- **Continuous Polling & Heartbeat**: Devices regularly sync with the master server, updating assignments dynamically and indicating live health metrics.

---

<div align="center">
  <p>Built with ❤️ and continuous learning.</p>
</div>
