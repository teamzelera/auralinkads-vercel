/**
 * localVideoDb.js
 * ────────────────────────────────────────────────────────────
 * IndexedDB helpers for:
 *   1. "local-videos"   — single-slot local video upload (existing)
 *   2. "received-files"  — phone-to-TV transferred files (new)
 *
 * DB:    auralink-db   (version 2)
 */

const DB_NAME = "auralink-db";
const DB_VERSION = 2;
const STORE_LOCAL = "local-videos";
const STORE_RECEIVED = "received-files";
const CURRENT_KEY = "current";

/** Open (or create/upgrade) the database. Returns a Promise<IDBDatabase>. */
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (e) => {
      const db = e.target.result;
      // v1 store
      if (!db.objectStoreNames.contains(STORE_LOCAL)) {
        db.createObjectStore(STORE_LOCAL, { keyPath: "id" });
      }
      // v2 store
      if (!db.objectStoreNames.contains(STORE_RECEIVED)) {
        const store = db.createObjectStore(STORE_RECEIVED, { keyPath: "id", autoIncrement: true });
        store.createIndex("created_at", "created_at", { unique: false });
      }
    };

    request.onsuccess = (e) => resolve(e.target.result);
    request.onerror  = (e) => reject(e.target.error);
  });
}


// ═══════════════════════════════════════════════════════════
// LOCAL VIDEO (single slot) — existing API unchanged
// ═══════════════════════════════════════════════════════════

export async function saveLocalVideo(file) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx    = db.transaction(STORE_LOCAL, "readwrite");
    const store = tx.objectStore(STORE_LOCAL);
    const req   = store.put({ id: CURRENT_KEY, file, name: file.name, savedAt: Date.now() });
    req.onsuccess = () => resolve();
    req.onerror   = (e) => reject(e.target.error);
  });
}

export async function getLocalVideoUrl() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx    = db.transaction(STORE_LOCAL, "readonly");
    const store = tx.objectStore(STORE_LOCAL);
    const req   = store.get(CURRENT_KEY);
    req.onsuccess = (e) => {
      const record = e.target.result;
      if (!record) return resolve(null);
      const url = URL.createObjectURL(record.file);
      resolve(url);
    };
    req.onerror = (e) => reject(e.target.error);
  });
}

export async function getLocalVideoRecord() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx    = db.transaction(STORE_LOCAL, "readonly");
    const store = tx.objectStore(STORE_LOCAL);
    const req   = store.get(CURRENT_KEY);
    req.onsuccess = (e) => resolve(e.target.result || null);
    req.onerror   = (e) => reject(e.target.error);
  });
}

export async function deleteLocalVideo() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx    = db.transaction(STORE_LOCAL, "readwrite");
    const store = tx.objectStore(STORE_LOCAL);
    const req   = store.delete(CURRENT_KEY);
    req.onsuccess = () => resolve();
    req.onerror   = (e) => reject(e.target.error);
  });
}


// ═══════════════════════════════════════════════════════════
// RECEIVED FILES (from phone transfer)
// ═══════════════════════════════════════════════════════════

/** Save a received file blob to IndexedDB. */
export async function saveReceivedFile(blob, name, fileType) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx    = db.transaction(STORE_RECEIVED, "readwrite");
    const store = tx.objectStore(STORE_RECEIVED);
    const req   = store.add({
      file: blob,
      file_name: name,
      file_type: fileType,
      file_size: blob.size,
      created_at: Date.now(),
    });
    req.onsuccess = (e) => resolve(e.target.result); // returns the auto-incremented id
    req.onerror   = (e) => reject(e.target.error);
  });
}

/** Get all received file records (without creating blob URLs). */
export async function getAllReceivedFiles() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx    = db.transaction(STORE_RECEIVED, "readonly");
    const store = tx.objectStore(STORE_RECEIVED);
    const req   = store.getAll();
    req.onsuccess = (e) => resolve(e.target.result || []);
    req.onerror   = (e) => reject(e.target.error);
  });
}

/** Get a blob URL for a specific received file by id. */
export async function getReceivedFileUrl(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx    = db.transaction(STORE_RECEIVED, "readonly");
    const store = tx.objectStore(STORE_RECEIVED);
    const req   = store.get(id);
    req.onsuccess = (e) => {
      const record = e.target.result;
      if (!record) return resolve(null);
      resolve(URL.createObjectURL(record.file));
    };
    req.onerror = (e) => reject(e.target.error);
  });
}

/** Delete a received file by id. */
export async function deleteReceivedFile(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx    = db.transaction(STORE_RECEIVED, "readwrite");
    const store = tx.objectStore(STORE_RECEIVED);
    const req   = store.delete(id);
    req.onsuccess = () => resolve();
    req.onerror   = (e) => reject(e.target.error);
  });
}
