export type Device = {
    id: string;
    name: string;
    ip_address: string; // Poprawiono z ipAddress na ip_address
    type: string;
    status: 'online' | 'offline' | 'error'; // Wartości zwracane przez monitoring w backendzie
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const fetchDevices = async (): Promise<Device[]> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/devices`);

    if (!res.ok) {
        throw new Error('Failed to fetch devices. Please try again later.');
    }

    return res.json();
};

export type CreateDeviceInput = {
    name: string;
    ip_address: string;
    device_type: string;
    vendor: string;
    model: string;
    os_version: string;
    location: string;
    is_active: boolean;
};

export const createDevice = async (deviceData: CreateDeviceInput): Promise<Device> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/devices`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(deviceData),
    });

    if (!res.ok) {
        throw new Error('Failed to create device');
    }

    return res.json();
};
