import Link from "next/link";
import { FiGrid, FiBarChart2, FiFileText, FiAlertTriangle, FiSettings } from 'react-icons/fi';

const Sidebar = () => {
  const navLinks = [
    { name: 'Devices', href: '/devices', icon: FiGrid },
    { name: 'Metrics', href: '/metrics', icon: FiBarChart2 },
    { name: 'Logs', href: '/logs', icon: FiFileText },
    { name: 'Alerts', href: '/alerts', icon: FiAlertTriangle },
    { name: 'Settings', href: '/settings', icon: FiSettings },
  ];

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col p-4">
      <div className="flex items-center justify-center h-16 border-b border-gray-700 mb-4">
        <h1 className="text-2xl font-bold text-indigo-400">SOTP</h1>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1">
        <ul>
          {navLinks.map((link) => (
            <li key={link.name} className="mb-2">
              <Link href={link.href} className="flex items-center p-3 rounded-lg hover:bg-gray-700 transition-colors duration-200">
                <span className="w-6 h-6 mr-3 flex items-center justify-center">
                  <link.icon size={24} color="currentColor" />
                </span>
                <span className="text-lg">{link.name}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer Section (optional) */}
      <div className="mt-auto">
        <p className="text-xs text-center text-gray-500">&copy; 2025 SOTP Platform</p>
      </div>
    </aside>
  );
};

export default Sidebar;
