import React from "react";


// Definicja komponentu strony
export default function HomePage() {
    return (
        // Zmieniamy tło na widoczny żółty, używamy p-10 i min-h-screen, aby pokryć całą stronę
        <main className="p-10 bg-[#E6E6FA] min-h-screen">

            <h1 className="text-5xl font-black text-purple-700 p-4 border-b-4 border-purple-900 flex justify-center">
                Welcome to the SOTP Platform!
            </h1>
            {/*
      <Link
        href="/devices"
        className="text-2xl text-blue-800 hover:text-blue-500 mt-8 block underline font-medium"
      >
        Przejdź do strony Urządzeń - (Devices)
      </Link>
*/}

            <div
                className="mt-10 p-5 bg-white shadow-lg rounded-lg max-w-2xl flex intems-center justify-center mx-auto">
                <p className="text-gray-700 flex justify-center">Many changes are coming! It is just the beginning.</p>
            </div>

        </main>
    );
}

