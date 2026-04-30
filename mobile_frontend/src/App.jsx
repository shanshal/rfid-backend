import { useEffect, useMemo, useRef, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import {
  assignDeviceRoom,
  getDeviceLogs,
  getDevices,
  getInstruments,
  getPendingDevices,
  getRooms,
  getUnknownScans,
  registerDevice,
  registerInstrument,
} from "./api";

function toMacCandidate(raw) {
  if (!raw) return "";
  const upper = raw.toUpperCase().trim();
  const withColons = upper.match(/([0-9A-F]{2}:){5}[0-9A-F]{2}/);
  if (withColons) return withColons[0];

  const compact = upper.replace(/[^0-9A-F]/g, "");
  if (compact.length === 12) {
    return compact.match(/.{1,2}/g).join(":");
  }
  return "";
}

function statusFromActivity(lastActivityAt) {
  if (!lastActivityAt) return "offline";
  const seconds = (Date.now() - new Date(lastActivityAt).getTime()) / 1000;
  return seconds <= 60 ? "online" : "stale";
}

function formatTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString();
}

function Shell({ children }) {
  const tabClass = ({ isActive }) => (isActive ? "active" : "");

  return (
    <div className="app-shell">
      <header className="topbar">
        <p className="eyebrow">RFID Operations</p>
        <h1>Mobile Console</h1>
      </header>
      <main className="content">{children}</main>
      <nav className="tabbar">
        <NavLink to="/devices/register" className={tabClass}>Device</NavLink>
        <NavLink to="/devices" className={tabClass}>Status</NavLink>
        <NavLink to="/instruments/register" className={tabClass}>Instrument</NavLink>
        <NavLink to="/instruments" className={tabClass}>Inventory</NavLink>
      </nav>
    </div>
  );
}

function QrMacScanner({ onMac }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const [error, setError] = useState("");
  const [active, setActive] = useState(false);

  const stop = () => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setActive(false);
  };

  const start = async () => {
    setError("");
    if (!("mediaDevices" in navigator) || !("getUserMedia" in navigator.mediaDevices)) {
      setError("Camera is not available on this browser.");
      return;
    }
    if (!("BarcodeDetector" in window)) {
      setError("QR detection is unavailable here. Use manual MAC input.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" } },
        audio: false,
      });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
      setActive(true);

      const detector = new window.BarcodeDetector({ formats: ["qr_code"] });
      timerRef.current = window.setInterval(async () => {
        if (!videoRef.current) return;
        try {
          const detected = await detector.detect(videoRef.current);
          if (!detected.length) return;
          const raw = detected[0].rawValue || "";
          const mac = toMacCandidate(raw);
          if (mac) {
            onMac(mac);
            stop();
          }
        } catch {
          // keep trying
        }
      }, 500);
    } catch {
      setError("Unable to access camera. Check permissions and try again.");
    }
  };

  useEffect(() => () => stop(), []);

  return (
    <section className="card">
      <h3>Scan Device MAC QR</h3>
      <p className="muted">Backend format: uppercase MAC with colons.</p>
      <video ref={videoRef} className="scanner" muted playsInline />
      <div className="row">
        <button type="button" onClick={start}>Start camera</button>
        {active && (
          <button type="button" className="secondary" onClick={stop}>
            Stop
          </button>
        )}
      </div>
      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}

function DeviceRegisterPage() {
  const [rooms, setRooms] = useState([]);
  const [form, setForm] = useState({ mac_address: "", name: "", room_id: "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getRooms().then((res) => setRooms(res.data || [])).catch(() => setRooms([]));
  }, []);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");
    const mac = toMacCandidate(form.mac_address);
    if (!mac) {
      setError("Enter a valid MAC address.");
      return;
    }
    try {
      const payload = {
        mac_address: mac,
        name: form.name.trim() || null,
        room_id: form.room_id ? Number(form.room_id) : null,
      };
      const res = await registerDevice(payload);
      setMessage(`Saved device #${res.data.id} (${res.data.mac_address}).`);
      setForm((f) => ({ ...f, mac_address: mac }));
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not register device.");
    }
  };

  return (
    <>
      <QrMacScanner onMac={(mac) => setForm((f) => ({ ...f, mac_address: mac }))} />
      <form className="card" onSubmit={submit}>
        <h3>Register Device</h3>
        <label>
          MAC address
          <input
            value={form.mac_address}
            onChange={(e) => setForm((f) => ({ ...f, mac_address: e.target.value }))}
            placeholder="AA:BB:CC:DD:EE:FF"
          />
        </label>
        <label>
          Name
          <input
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            placeholder="Room scanner"
          />
        </label>
        <label>
          Room
          <select value={form.room_id} onChange={(e) => setForm((f) => ({ ...f, room_id: e.target.value }))}>
            <option value="">Unassigned</option>
            {rooms.map((room) => (
              <option key={room.id} value={room.id}>{room.name}</option>
            ))}
          </select>
        </label>
        <button type="submit">Save device</button>
        {message ? <p className="ok">{message}</p> : null}
        {error ? <p className="error">{error}</p> : null}
      </form>
    </>
  );
}

function DevicesStatusPage() {
  const [devices, setDevices] = useState([]);
  const [pending, setPending] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState(null);
  const [logs, setLogs] = useState([]);
  const [roomPick, setRoomPick] = useState({});
  const [error, setError] = useState("");

  const roomsById = useMemo(() => Object.fromEntries(rooms.map((r) => [r.id, r.name])), [rooms]);

  const loadAll = async () => {
    setError("");
    try {
      const [deviceRes, pendingRes, roomRes] = await Promise.all([getDevices(), getPendingDevices(), getRooms()]);
      setDevices(deviceRes.data || []);
      setPending(pendingRes.data || []);
      setRooms(roomRes.data || []);
      if (!selectedDeviceId && deviceRes.data?.length) {
        setSelectedDeviceId(deviceRes.data[0].id);
      }
    } catch {
      setError("Could not load device status.");
    }
  };

  useEffect(() => {
    loadAll();
    const timer = window.setInterval(loadAll, 8000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!selectedDeviceId) return;
    getDeviceLogs(selectedDeviceId, 40)
      .then((res) => setLogs(res.data || []))
      .catch(() => setLogs([]));
  }, [selectedDeviceId, devices]);

  const assign = async (device) => {
    const picked = Number(roomPick[device.id]);
    if (!picked) return;
    try {
      await assignDeviceRoom(device.id, picked, device.name);
      await loadAll();
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not assign device room.");
    }
  };

  return (
    <>
      <section className="card">
        <h3>Devices</h3>
        <p className="muted">Pending devices: {pending.length}</p>
        {devices.map((device) => {
          const status = statusFromActivity(device.last_activity_at);
          return (
            <article
              key={device.id}
              className={`list-item ${selectedDeviceId === device.id ? "active" : ""}`}
              onClick={() => setSelectedDeviceId(device.id)}
            >
              <div>
                <strong>{device.name}</strong>
                <p className="mono">{device.mac_address}</p>
                <p className="muted">Room: {device.room_id ? roomsById[device.room_id] || `#${device.room_id}` : "Unassigned"}</p>
              </div>
              <span className={`badge ${status}`}>{status}</span>
              {!device.room_id ? (
                <div className="row">
                  <select
                    onClick={(e) => e.stopPropagation()}
                    value={roomPick[device.id] || ""}
                    onChange={(e) => setRoomPick((state) => ({ ...state, [device.id]: e.target.value }))}
                  >
                    <option value="">Assign room</option>
                    {rooms.map((room) => (
                      <option key={room.id} value={room.id}>{room.name}</option>
                    ))}
                  </select>
                  <button type="button" onClick={(e) => { e.stopPropagation(); assign(device); }}>
                    Save
                  </button>
                </div>
              ) : null}
              <p className="muted">IP: {device.local_ip || "-"} · Topic: {device.scan_topic || "-"}</p>
            </article>
          );
        })}
        {error ? <p className="error">{error}</p> : null}
      </section>

      <section className="card">
        <h3>Selected Device Logs</h3>
        {logs.length === 0 ? <p className="muted">No logs yet.</p> : null}
        {logs.map((log) => (
          <article key={log.id} className="log-line">
            <p>
              <strong>{log.outcome}</strong> · {formatTime(log.backend_received_at)}
            </p>
            <p className="mono">RFID: {log.rfid_uid || "-"}</p>
          </article>
        ))}
      </section>
    </>
  );
}

function InstrumentRegisterPage() {
  const [rooms, setRooms] = useState([]);
  const [unknown, setUnknown] = useState([]);
  const [form, setForm] = useState({ rfid: "", name: "", room_id: "", status: "available" });
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  const load = async () => {
    try {
      const [roomsRes, unknownRes] = await Promise.all([getRooms(), getUnknownScans()]);
      setRooms(roomsRes.data || []);
      setUnknown(unknownRes.data || []);
    } catch {
      setUnknown([]);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (event) => {
    event.preventDefault();
    setErr("");
    setMsg("");
    if (!form.rfid.trim() || !form.room_id) {
      setErr("RFID and room are required.");
      return;
    }
    try {
      const payload = {
        rfid: form.rfid.trim(),
        name: form.name.trim() || `Instrument-${form.rfid.trim()}`,
        room_id: Number(form.room_id),
        status: form.status,
      };
      const res = await registerInstrument(payload);
      setMsg(`Instrument #${res.data.id} registered.`);
      await load();
    } catch (error) {
      setErr(error?.response?.data?.detail || "Could not register instrument.");
    }
  };

  return (
    <>
      <section className="card">
        <h3>Unknown Scans</h3>
        <p className="muted">Tap one to prefill RFID.</p>
        {unknown.slice(0, 12).map((trace) => (
          <button
            key={trace.id}
            className="chip"
            type="button"
            onClick={() => setForm((state) => ({ ...state, rfid: trace.rfid_uid || "" }))}
          >
            {trace.rfid_uid || "-"} · {formatTime(trace.backend_received_at)}
          </button>
        ))}
      </section>

      <form className="card" onSubmit={submit}>
        <h3>Register Instrument</h3>
        <label>
          RFID UID
          <input value={form.rfid} onChange={(e) => setForm((s) => ({ ...s, rfid: e.target.value }))} />
        </label>
        <label>
          Name
          <input value={form.name} onChange={(e) => setForm((s) => ({ ...s, name: e.target.value }))} />
        </label>
        <label>
          Room
          <select value={form.room_id} onChange={(e) => setForm((s) => ({ ...s, room_id: e.target.value }))}>
            <option value="">Select room</option>
            {rooms.map((room) => (
              <option key={room.id} value={room.id}>{room.name}</option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select value={form.status} onChange={(e) => setForm((s) => ({ ...s, status: e.target.value }))}>
            <option value="available">available</option>
            <option value="in_use">in_use</option>
            <option value="sterilizing">sterilizing</option>
            <option value="contaminated">contaminated</option>
          </select>
        </label>
        <button type="submit">Save instrument</button>
        {msg ? <p className="ok">{msg}</p> : null}
        {err ? <p className="error">{err}</p> : null}
      </form>
    </>
  );
}

function InstrumentsPage() {
  const [items, setItems] = useState([]);
  const [rooms, setRooms] = useState([]);

  const roomsById = useMemo(() => Object.fromEntries(rooms.map((r) => [r.id, r.name])), [rooms]);

  const load = async () => {
    const [instrumentsRes, roomsRes] = await Promise.all([getInstruments(), getRooms()]);
    setItems(instrumentsRes.data || []);
    setRooms(roomsRes.data || []);
  };

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 10000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <section className="card">
      <h3>Instrument Status and Location</h3>
      {items.map((instrument) => (
        <article key={instrument.id} className="list-item">
          <div>
            <strong>{instrument.name}</strong>
            <p className="mono">{instrument.rfid}</p>
            <p className="muted">Room: {roomsById[instrument.current_room] || `#${instrument.current_room}`}</p>
          </div>
          <span className="badge neutral">{instrument.status}</span>
        </article>
      ))}
    </section>
  );
}

export default function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/" element={<DeviceRegisterPage />} />
        <Route path="/devices/register" element={<DeviceRegisterPage />} />
        <Route path="/devices" element={<DevicesStatusPage />} />
        <Route path="/instruments/register" element={<InstrumentRegisterPage />} />
        <Route path="/instruments" element={<InstrumentsPage />} />
      </Routes>
    </Shell>
  );
}
