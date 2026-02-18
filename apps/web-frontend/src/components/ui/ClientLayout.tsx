// src/app/components/ClientLayout.tsx

"use client"; // <--- Ta dyrektywa jest teraz tutaj!

import { useState } from "react";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

// Ten komponent przyjmuje 'children' i je renderuje
export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden">

      {/* Sidebar - Desktop */}
      <div className="hidden md:flex">
        <Sidebar />
      </div>

      {/* Sidebar - Mobile */}
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

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <Navbar onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 p-4 sm:p-6 md:p-8 overflow-y-auto">
          {children} {/* Tutaj renderuje się treść strony */}
        </main>
      </div>
    </div>
  );
}
