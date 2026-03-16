// src/components/ui/Navbar.tsx
import React from "react";
import { FiMenu, FiUser } from "react-icons/fi";
import Link from "next/link";

type NavbarProps = {
  onMenuClick: () => void;
};

export default function Navbar({ onMenuClick }: NavbarProps) {
  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 md:px-6 flex-shrink-0">
      <Link href="/" className="flex items-center gap-3">
        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
          S
        </div>
        <span className="text-gray-900 font-semibold hidden sm:block">SOTP Platform</span>
      </Link>

      <div className="flex items-center gap-2">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
          aria-label="Open menu"
        >
          <FiMenu size={20} />
        </button>
        <button
          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
          aria-label="User profile"
        >
          <FiUser size={20} />
        </button>
      </div>
    </header>
  );
}
