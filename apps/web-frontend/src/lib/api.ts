// src/lib/api.ts

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// ─── Types ────────────────────────────────────────────────────────────────────

export type DeviceType = "router" | "switch" | "server" | "firewall";
export type DeviceStatus = "Online" | "Offline" | "Warning";

export interface Device {
  id: string;
  name: string;
  ip_address: string;
  device_type: DeviceType;
  vendor: string;
  model: string;
  os_version: string;
  location: string;
  is_active: boolean;
  status?: DeviceStatus;
  created_at?: string;
}

export interface CreateDeviceInput {
  name: string;
  ip_address: string;
  device_type: string;
  vendor: string;
  model: string;
  os_version: string;
  location: string;
  is_active: boolean;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const msg = await res.text().catch(() => "Unknown error");
    throw new Error(`API error ${res.status}: ${msg}`);
  }

  return res.json() as Promise<T>;
}

// ─── Devices ──────────────────────────────────────────────────────────────────

export const fetchDevices = (): Promise<Device[]> =>
  apiFetch<Device[]>("/devices");

export const fetchDevice = (id: string): Promise<Device> =>
  apiFetch<Device>(`/devices/${id}`);

export const createDevice = (data: CreateDeviceInput): Promise<Device> =>
  apiFetch<Device>("/devices", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const deleteDevice = (id: string): Promise<void> =>
  apiFetch<void>(`/devices/${id}`, { method: "DELETE" });
