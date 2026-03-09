# AuraLink API Documentation

This document serves as the complete reference for the AuraLink Digital Signage Backend APIs. 
The API is split into Admin APIs (secured by JWT) and Device APIs (secured by static Tokens).

## Base URL
`http://localhost:8000/api`

## Interactive Documentation
Interactive API docs powered by Swagger/drf-yasg are available locally at:
- **Swagger UI:** `/swagger/`
- **ReDoc:** `/redoc/`

---

## 1. Admin APIs
Authentication: `Authorization: Bearer <JWT Token>`

### POST `/api/auth/login/` *(corresponds to Admin Login)*
Authenticate an admin user and return JWT tokens.
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "username": "admin",
    "password": "password"
  }
  ```
- **Response:**
  ```json
  {
    "refresh": "eyJhbG...",
    "access": "eyJhbG..."
  }
  ```

### POST `/api/admin/upload-video/`
Upload a new video file to Cloudinary and register it in the database.
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file`: (File) The video file.
  - `title`: (String) Video title.
- **Response:**
  ```json
  {
    "id": "uuid",
    "title": "Welcome Screen",
    "cloudinary_url": "https://res.cloudinary.com/...",
    "thumbnail": "https://res.cloudinary.com/...",
    "duration": 120.0
  }
  ```

### GET `/api/devices/` *(corresponds to Admin Devices)*
List all registered devices and their current status.
- **Method:** `GET`
- **Response:**
  ```json
  [
    {
      "id": "uuid",
      "name": "Lobby Display",
      "device_code": "AUR-1234",
      "location": "Front Desk",
      "status": "online",
      "last_seen": "2026-03-08T12:00:00Z"
    }
  ]
  ```

### POST `/api/devices/generate-code/` *(corresponds to Create Device)*
Register a new device and generate its unique pairing code.
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "name": "Lobby Display",
    "location": "Front Desk"
  }
  ```
- **Response:**
  ```json
  {
    "id": "uuid",
    "name": "Lobby Display",
    "device_code": "AUR-1234",
    "status": "offline"
  }
  ```

### POST `/api/playlists/assignments/` *(corresponds to Assign Playlist)*
Assign a specific playlist to a device.
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "device_id": "uuid",
    "playlist_id": "uuid",
    "loop_enabled": true
  }
  ```
- **Response:**
  ```json
  {
    "id": "uuid",
    "device": "uuid",
    "playlist": "uuid",
    "loop_enabled": true,
    "active": true
  }
  ```

---

## 2. Device APIs
Authentication: `Authorization: Device <DeviceToken>` (except `/api/devices/authenticate/`)

### POST `/api/devices/authenticate/`
Exchange a short device pairing code for a persistent device token.
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "device_code": "AUR-1234"
  }
  ```
- **Response:**
  ```json
  {
    "device_token": "random_secure_token_string"
  }
  ```

### GET `/api/device/get-playlist/`
Fetch the active playlist assignment and Cloudinary video URLs for a specific authenticated device.
- **Method:** `GET`
- **Response:**
  ```json
  {
    "assignment": {
      "id": "uuid",
      "loop_enabled": true,
      "playlist": {
        "id": "uuid",
        "name": "Morning Loop",
        "videos": [
          {
            "id": "uuid",
            "order": 1,
            "video": {
              "title": "Welcome",
              "cloudinary_url": "https://cdn.example.com/video1.mp4"
            }
          }
        ]
      }
    }
  }
  ```

### POST `/api/devices/heartbeat/`
Register a device heartbeat to mark it as 'online'.
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "status": "playing"
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "timestamp": "2026-03-08T12:05:00Z"
  }
  ```

### POST `/api/device/playback-log`
*Note: This specific logging endpoint is not yet fully implemented in the current production release.*
Logs analytics for video playback success/failures.
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "video_id": "uuid",
    "action": "started | finished | error",
    "timestamp": "2026-03-08T12:05:00Z"
  }
  ```

---

## 3. Video Management APIs
Authentication: `Authorization: Bearer <JWT Token>`
- `GET /api/videos/` - List all uploaded videos
- `DELETE /api/videos/<id>/` - Delete a video
- `GET /api/videos/cloudinary-signature/` - Get signed credentials for direct upload

## 4. Playlist APIs
Authentication: `Authorization: Bearer <JWT Token>`
- `GET /api/playlists/` - List all playlists and their videos
- `POST /api/playlists/` - Create a new playlist
- `GET /api/playlists/<id>/` - Get playlist details
- `DELETE /api/playlists/<id>/` - Delete a playlist

## 5. Analytics APIs
Authentication: `Authorization: Bearer <JWT Token>`
- `GET /api/analytics/dashboard/` - High-level metrics (online devices, total videos, etc.)
- `GET /api/analytics/uptime/` - Detailed per-device 24h uptime statistics
