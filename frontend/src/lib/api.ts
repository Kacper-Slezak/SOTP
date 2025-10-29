export type Device = {
  id: string;
  name: string;
  ipAddress: string;
  type: string;
  status: 'Online' | 'Offline' | 'Warning';
};

// Funkcja do pobierania danych
export const fetchDevices = async (): Promise<Device[]> => {
  const res = await fetch('/api/v1/devices');
  if (!res.ok) {
    throw new Error('Failed to fetch devices. Please try again later.');
  }
  return res.json();
};