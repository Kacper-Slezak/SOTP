// src/app/page.tsx
import Link from "next/link";
import { FiGrid, FiBarChart2, FiFileText, FiAlertTriangle } from "react-icons/fi";

const cards = [
  {
    label: "Devices",
    href: "/devices",
    icon: FiGrid,
    desc: "Manage network devices, view status and details.",
    color: "bg-indigo-500",
  },
  {
    label: "Metrics",
    href: "/metrics",
    icon: FiBarChart2,
    desc: "Monitor performance metrics and trends.",
    color: "bg-emerald-500",
  },
  {
    label: "Logs",
    href: "/logs",
    icon: FiFileText,
    desc: "Browse system and application logs.",
    color: "bg-amber-500",
  },
  {
    label: "Alerts",
    href: "/alerts",
    icon: FiAlertTriangle,
    desc: "Active alerts and notification rules.",
    color: "bg-rose-500",
  },
];

export default function HomePage() {
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">
          Welcome to the System Observability &amp; Telemetry Platform.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map(({ label, href, icon: Icon, desc, color }) => (
          <Link
            key={label}
            href={href}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col gap-3 hover:shadow-md transition-shadow"
          >
            <div
              className={`${color} w-10 h-10 rounded-lg flex items-center justify-center text-white`}
            >
              <Icon size={20} />
            </div>
            <div>
              <p className="font-semibold text-gray-800">{label}</p>
              <p className="text-sm text-gray-500 mt-0.5">{desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
