import Image from "next/image";
import React from "react";
import { FiMenu, FiUser } from "react-icons/fi";
import Link from 'next/link';

type NavbarProps = {
    onMenuClick: () => void;
};

const Navbar = ({ onMenuClick }: NavbarProps) => {
    return (
        <header className="bg-white shadow-sm h-16 flex items-center justify-between px-4 md:px-6 border-b border-gray-200">
            
            <Link href="/" className="flex items-center gap-x-3">
                <Image
                    src="/SOTP1(1).png"
                    alt="SOTP Logo"
                    width={48}
                    height={48}
                    className="rounded-md"
                />
                <h1 className="text-xl font-semibold text-gray-800 hidden md:block">
                    System Observability & Telemetry Platform
                </h1>
                <h1 className="text-xl font-semibold text-gray-800 hidden sm:block md:hidden">
                    SOTP
                </h1>
            </Link>

            
            <div className="flex items-center gap-x-2">
                <button
                    onClick={onMenuClick}
                    className="md:hidden p-2 rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-800 transition-colors duration-200"
                    aria-label="Open menu"
                >
                    <FiMenu size={24} />
                </button>
                <button
                    className="p-2 rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-800 transition-colors duration-200"
                    aria-label="User profile"
                >
                    <FiUser size={24} />
                </button>
            </div>
        </header>
    );
};

export default Navbar;