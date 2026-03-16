"use client";

// src/components/ui/Sidebar.tsx
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FiGrid,
  FiBarChart2,
  FiFileText,
  FiAlertTriangle,
  FiSettings,
} from "react-icons/fi";

const navLinks = [
  { name: "Devices", href: "/devices", icon: FiGrid },
  { name: "Metrics", href: "/metrics", icon: FiBarChart2 },
  { name: "Logs", href: "/logs", icon: FiFileText },
  { name: "Alerts", href: "/alerts", icon: FiAlertTriangle },
  { name: "Settings", href: "/settings", icon: FiSettings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-gray-900 text-white flex flex-col h-full">
      {/* Logo */}
      <div className="h-16 flex items-center px-4 border-b border-gray-700 flex-shrink-0">
        <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center text-white font-bold text-sm mr-3">
          S
        </div>
        <span className="font-semibold text-white">SOTP</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1">
        {navLinks.map(({ name, href, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={name}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-indigo-600 text-white"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <Icon size={18} />
              {name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-700">
        <p className="text-xs text-gray-500 text-center">© 2025 SOTP Platform</p>
      </div>
    </aside>
  );
}
