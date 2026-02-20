"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createDevice, CreateDeviceInput } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

export default function NewDevicePage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState<CreateDeviceInput>({
    name: "",
    ip_address: "",
    device_type: "",
    vendor: "",
    model: "",
    os_version: "",
    location: "",
    is_active: true,
  });

  const mutation = useMutation({
    mutationFn: createDevice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["devices"] });
      router.push("/devices");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Dodaj nowe urządzenie</h1>
        <Button variant="outline" onClick={() => router.push("/devices")}>
          Anuluj
        </Button>
      </div>

      <div className="border rounded-lg bg-white p-6 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-4">

          <div className="grid grid-cols-2 gap-4">
            {/* Nazwa */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-1">Nazwa urządzenia</label>
              <input
                id="name"
                required
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="np. Router Główny"
                autoComplete="off"
                className="w-full border rounded-md p-2"
              />
            </div>

            {/* Adres IP */}
            <div>
              <label htmlFor="ip_address" className="block text-sm font-medium mb-1">Adres IP</label>
              <input
                id="ip_address"
                required
                type="text"
                name="ip_address"
                value={formData.ip_address}
                onChange={handleChange}
                placeholder="np. 192.168.1.1"
                autoComplete="off"
                className="w-full border rounded-md p-2"
              />
            </div>

            {/* Producent (Vendor) */}
            <div>
              <label htmlFor="vendor" className="block text-sm font-medium mb-1">Producent (Vendor)</label>
              <input
                id="vendor"
                required
                type="text"
                name="vendor"
                value={formData.vendor}
                onChange={handleChange}
                placeholder="np. Cisco"
                autoComplete="off"
                className="w-full border rounded-md p-2"
              />
            </div>

            {/* Model */}
            <div>
              <label htmlFor="model" className="block text-sm font-medium mb-1">Model</label>
              <input
                id="model"
                required
                type="text"
                name="model"
                value={formData.model}
                onChange={handleChange}
                placeholder="np. Catalyst 9300"
                autoComplete="off"
                className="w-full border rounded-md p-2"
              />
            </div>

            {/* Wersja OS */}
            <div>
              <label htmlFor="os_version" className="block text-sm font-medium mb-1">Wersja OS</label>
              <input
                id="os_version"
                required
                type="text"
                name="os_version"
                value={formData.os_version}
                onChange={handleChange}
                placeholder="np. IOS XE 17.3.1"
                autoComplete="off"
                className="w-full border rounded-md p-2"
              />
            </div>

            {/* Lokalizacja */}
            <div>
              <label htmlFor="location" className="block text-sm font-medium mb-1">Lokalizacja</label>
              <input
                id="location"
                required
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="np. Serwerownia A"
                autoComplete="off"
                className="w-full border rounded-md p-2"
              />
            </div>

            {/* Typ */}
            <div>
              <label htmlFor="device_type" className="block text-sm font-medium mb-1">Typ</label>
              <select
                id="device_type"
                required
                name="device_type"
                value={formData.device_type}
                onChange={handleChange}
                autoComplete="off"
                className="w-full border rounded-md p-2"
              >
                <option value="" disabled>Wybierz typ...</option>
                <option value="router">Router</option>
                <option value="switch">Switch</option>
                <option value="server">Serwer</option>
                <option value="firewall">Firewall</option>
              </select>
            </div>
          </div>

          {mutation.isError && (
            <p className="text-red-500 text-sm mt-2">
              Wystąpił błąd: {(mutation.error as Error).message}
            </p>
          )}

          <div className="pt-4 flex justify-end">
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Zapisz urządzenie
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
