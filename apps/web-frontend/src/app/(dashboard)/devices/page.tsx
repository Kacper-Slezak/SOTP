"use client";

import {useQuery} from "@tanstack/react-query";
import {Device, fetchDevices} from "@/lib/api"; // Upewnij się, że ta funkcja istnieje
import {useRouter} from "next/navigation";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from "@/components/ui/table";
import {Button} from "@/components/ui/button";
import {Loader2, AlertCircle} from "lucide-react";

export default function DevicesPage() {
    const router = useRouter();

    // Integracja React Query [Akceptacja: React Query + GET /api/v1/devices]
    const {data: devices, isLoading, isError, error} = useQuery({
        queryKey: ["devices"],
        queryFn: fetchDevices,
    });

    // Obsługa stanu ładowania [Akceptacja: Loading state]
    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary"/>
            </div>
        );
    }

    // Obsługa stanu błędu [Akceptacja: Error state]
    if (isError) {
        return (
            <div className="flex h-full flex-col items-center justify-center text-destructive">
                <AlertCircle className="mb-2 h-10 w-10"/>
                <p>Wystąpił błąd podczas pobierania urządzeń: {(error as Error).message}</p>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold">Urządzenia</h1>
                {/* Przycisk nawigacji [Akceptacja: Add Device button] */}
                <Button onClick={() => router.push("/devices/new")}>
                    Dodaj Urządzenie
                </Button>
            </div>

            {/* Tabela shadcn/ui [Akceptacja: Table component + kolumny] */}
            <div className="border rounded-lg">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>IP Address</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {devices?.map((device: Device) => (
                            <TableRow key={device.id}>
                                <TableCell className="font-medium">{device.name}</TableCell>
                                <TableCell>{device.ip_address}</TableCell>
                                <TableCell>{device.type}</TableCell>
                                <TableCell>
                  <span
                      className={`px-2 py-1 rounded text-xs ${device.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {device.status}
                  </span>
                                </TableCell>
                                <TableCell className="text-right">
                                    <Button variant="ghost" size="sm">Edit</Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
