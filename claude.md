# AuraLink — Project Constitution (claude.md)

> This is the authoritative reference document for the AuraLink system.
> All architecture decisions, data schemas, and behavior rules are defined here.
> **If any logic changes, this document MUST be updated first.**

---

## 1. System Architecture

AuraLink is a **Digital Signage Management Platform** built on the A.N.T. 3-Layer Architecture:

```
Layer 1 — Architecture  →  SOPs, rules, behavior contracts
Layer 2 — Navigation    →  Django URL routing, API gateway
Layer 3 — Tools         →  Atomic Python utilities
```

### High-Level Flow
```
Admin (React Dashboard)
  │
  ├── REST API (DRF) → PostgreSQL
  │         │
  │         └── Cloudinary (video storage)
  │
  └── WebSocket (Django Channels) → Django Channels Layer (In-Memory / Redis)

Device (React Player)
  │
  ├── Device Auth (code-based token)
  ├── REST API (poll assignment every 60s)
  └── Heartbeat API (ping every 30s)
```

---

## 2. Authentication Model

### Admin Authentication
- Library: `djangorestframework-simplejwt`
- Flow: Admin registers → Login returns `access` + `refresh` JWT tokens
- Token lifetime: Access = 60 min, Refresh = 7 days
- All admin API endpoints require `Authorization: Bearer <access_token>`

### Device Authentication
- Flow: Admin generates a unique device code → Device submits code to `/api/devices/authenticate/`
- On success: Server returns a **device token** (opaque token stored in `Device.auth_token`)
- All device API endpoints require `Authorization: Device <device_token>`
- Device token does NOT expire — it is invalidated only when the device is deleted or deactivated by admin

---

## 3. Data Schemas

### Device
```python
class Device(models.Model):
    id           = UUIDField(primary_key=True, default=uuid4)
    name         = CharField(max_length=200)
    device_code  = CharField(max_length=8, unique=True)   # e.g. "AUR-4X9K"
    auth_token   = CharField(max_length=64, unique=True, blank=True)
    location     = CharField(max_length=300, blank=True)
    status       = CharField(choices=["online", "offline"], default="offline")
    last_seen    = DateTimeField(null=True)
    is_active    = BooleanField(default=True)
    created_at   = DateTimeField(auto_now_add=True)
```

### Video
```python
class Video(models.Model):
    id              = UUIDField(primary_key=True, default=uuid4)
    title           = CharField(max_length=300)
    cloudinary_url  = URLField()
    thumbnail       = URLField(blank=True)
    duration        = FloatField(default=0)           # seconds
    uploaded_by     = ForeignKey(User, on_delete=SET_NULL, null=True)
    created_at      = DateTimeField(auto_now_add=True)
```

### Playlist
```python
class Playlist(models.Model):
    id          = UUIDField(primary_key=True, default=uuid4)
    name        = CharField(max_length=300)
    created_by  = ForeignKey(User, on_delete=SET_NULL, null=True)
    created_at  = DateTimeField(auto_now_add=True)
```

### PlaylistVideo (ordered join table)
```python
class PlaylistVideo(models.Model):
    playlist  = ForeignKey(Playlist, on_delete=CASCADE)
    video     = ForeignKey(Video, on_delete=CASCADE)
    order     = PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = [["playlist", "video"]]
```

### DeviceAssignment
```python
class DeviceAssignment(models.Model):
    device        = OneToOneField(Device, on_delete=CASCADE)
    playlist      = ForeignKey(Playlist, on_delete=SET_NULL, null=True)
    loop_enabled  = BooleanField(default=True)
    active        = BooleanField(default=True)
    start_time    = TimeField(null=True, blank=True)   # scheduling
    end_time      = TimeField(null=True, blank=True)
    updated_at    = DateTimeField(auto_now=True)
```

### Heartbeat
```python
class Heartbeat(models.Model):
    device     = ForeignKey(Device, on_delete=CASCADE, related_name="heartbeats")
    timestamp  = DateTimeField(auto_now_add=True)
    status     = CharField(max_length=20, default="playing")  # "playing", "idle", "error"
```

---

## 4. Device Behavior Rules (SOP)

### Device Boot Sequence
1. Device opens React Player app
2. Check local storage for `device_token`
3. If no token → show **Device Login Screen** (enter device code)
4. If token exists → fetch assignment from API → begin playback

### Playback Rules
- Device plays the assigned playlist in `order` sequence
- When last video ends → loop back to first (if `loop_enabled = true`)
- If no assignment → show idle screen with AuraLink logo

### Heartbeat Rules
- Device sends `POST /api/devices/heartbeat/` every **30 seconds**
- Payload: `{ "status": "playing" | "idle" | "error" }`
- Server updates `Device.last_seen` and `Device.status = "online"`
- If no heartbeat for **90 seconds** → server marks device as `"offline"`

### Assignment Polling
- Device polls `GET /api/devices/me/assignment/` every **60 seconds**
- If assignment changes → device reloads playlist immediately

### Device UI Rules
- Full-screen locked video player
- Only UI element: small gear (⚙) icon in top-right corner
- Settings menu contains: Logout, Delete Device, About, Terms, Contact
- No navigation, no address bar, no user controls on video

---

## 5. Admin SOP

### Onboarding a New Screen
1. Admin goes to Devices → "Generate Code"
2. System creates a Device record with status=`offline`, is_active=`true`
3. Admin sees the 8-character code (e.g. `AUR-4X9K`)
4. Operator enters code on the physical screen
5. Device authenticates → status becomes `online`

### Content Assignment
1. Admin uploads video(s) via Videos page → Cloudinary stores file
2. Admin creates a Playlist, adds videos in order
3. Admin goes to Devices → selects device → "Assign Playlist"
4. Device picks up new assignment within 60 seconds

### Scheduling
- Admin can set `start_time` and `end_time` on a DeviceAssignment
- Device checks current time against schedule on each poll
- Outside schedule window → device shows idle screen

---

## 6. API Design Rules
- All endpoints are versioned under `/api/`
- Auth errors return `401 Unauthorized`
- Validation errors return `400 Bad Request` with field errors
- All timestamps are returned in ISO 8601 UTC format
- UUIDs are used for all primary keys
- Responses are camelCase in JSON (using `djangorestframework-camel-case`)

---

## 7. Real-time (WebSocket) Rules
- Backend: Django Channels with `InMemoryChannelLayer` (dev) / Redis (prod)
- Endpoint: `ws/devices/status/`
- Admin dashboard subscribes on load
- Server broadcasts device status changes in real time
- Message format: `{ "type": "device_status", "device_id": "...", "status": "online"|"offline" }`
