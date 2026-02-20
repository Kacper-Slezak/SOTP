"use client";

import { useState } from "react";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
// 1. Import QueryClient i Provider z React Query
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  
  // Nowa instancja klienta zapapytań (QueryClient)
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen overflow-hidden">

        <div className="hidden md:flex">
          <Sidebar />
        </div>

        {isSidebarOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <div onClick={e => e.stopPropagation()} className="absolute top-0 left-0 h-full">
              <Sidebar />
            </div>
          </div>
        )}

        <div className="flex-1 flex flex-col">
          <Navbar onMenuClick={() => setSidebarOpen(true)} />
          <main className="flex-1 p-4 sm:p-6 md:p-8 overflow-y-auto">
            {children}
          </main>
        </div>
      </div>
    </QueryClientProvider>
  );
}
