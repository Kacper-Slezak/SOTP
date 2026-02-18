// frontend/src/app/layout.tsx
import type { Metadata } from "next";
//import {useState} from "react";
import { Inter } from "next/font/google";
import "./globals.css";
import ClientLayout from "@/components/ui/ClientLayout";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SOTP Platform",
  description: "System Observability & Telemetry Platform",
};

// Upewnij się, że "export default" jest tutaj, przed funkcją
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  //const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <html lang="pl">
      <body className={`${inter.className} bg-gray-100`}>
        <ClientLayout>
          {children}
        </ClientLayout>
      </body>
    </html>
  );
}
