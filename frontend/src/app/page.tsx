import Link from "next/link";
import React from "react";

// Definicja komponentu strony
export default function HomePage() {
  return (
    // Zmieniamy tło na widoczny żółty, używamy p-10 i min-h-screen, aby pokryć całą stronę
    <main className="p-10 bg-yellow-200 min-h-screen">

      {/* Zmieniamy kolor tekstu na ciemny fiolet (700).
        Używamy większego tekstu (text-6xl) i grubego pogrubienia (font-black).
      */}
      <h1 className="text-6xl font-black text-purple-700 p-4 border-b-4 border-purple-900">
        Tailwind Działa!
      </h1>

      {/* Link zostawiamy z niebieskim, ale zwiększamy jego kontrast i margines górny */}
      <Link
        href="/devices"
        className="text-2xl text-blue-800 hover:text-blue-500 mt-8 block underline font-medium"
      >
        Przejdź do strony Urządzeń - (Devices)
      </Link>

      {/* Dodatkowy element, żeby pokazać tło */}
      <div className="mt-10 p-5 bg-white shadow-lg rounded-lg max-w-sm">
        <p className="text-gray-700">To jest element z tłem i cieniem.</p>
      </div>

    </main>
  );
}
