# AuraLink — Findings Log

## 2026-03-08 — Initial Architecture Decisions

### Decision: SQLite for Development
Using SQLite during local development for simplicity. Will switch to PostgreSQL for production.
Schema is identical — only DATABASE URL changes.

### Decision: UUID Primary Keys
All models use UUID PKs to support distributed device IDs and prevent enumeration attacks.

### Decision: Device Token (not JWT) for Device Auth
Devices use an opaque token stored in the database rather than JWT because:
- Devices are long-lived sessions (days/weeks)
- Tokens can be revoked instantly by the admin
- No need for refresh token complexity on device side

### Decision: InMemoryChannelLayer for Dev WebSockets
Using Django's built-in InMemoryChannelLayer for development WebSockets.
Redis channel layer required for production multi-process deployment.

### Decision: Cloudinary for Video Storage
Cloudinary handles transcoding, CDN delivery, and thumbnail generation automatically.
Avoids need to run ffmpeg on the server.

### Decision: 30s Heartbeat / 90s Offline Threshold
- 30s heartbeat = low overhead, near real-time status
- 90s threshold = allows one missed heartbeat before marking offline
- This is a 3x tolerance window (industry standard)

### Decision: Assignment Polling Every 60s
WebSockets handle status display. Polling handles content assignment updates.
Keeps device logic simple without requiring persistent WS connection on device.
