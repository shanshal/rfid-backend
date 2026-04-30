import axios from "axios";

const API_BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");
const ACTOR = import.meta.env.VITE_ACTOR || "mobile-admin";

const api = axios.create({
  baseURL: API_BASE,
});

export const getRooms = () => api.get("/rooms/");
export const getDevices = () => api.get("/devices/");
export const getPendingDevices = () => api.get("/devices/pending");
export const getDeviceLogs = (deviceId, limit = 50) => api.get(`/devices/${deviceId}/logs`, { params: { limit } });
export const registerDevice = (payload) => api.post("/devices/register", payload, { params: { actor: ACTOR } });
export const assignDeviceRoom = (deviceId, roomId, name) =>
  api.put(`/devices/${deviceId}/assign-room`, { room_id: roomId, name: name || null }, { params: { actor: ACTOR } });

export const getInstruments = () => api.get("/instruments/");
export const registerInstrument = (payload) => api.post("/instruments/", payload, { params: { actor: ACTOR } });
export const getUnknownScans = (limit = 30) =>
  api.get("/diagnostics/traces", { params: { outcome: "unknown_rfid", limit } });

export default api;
