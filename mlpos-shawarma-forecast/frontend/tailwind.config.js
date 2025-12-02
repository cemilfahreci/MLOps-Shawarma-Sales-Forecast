/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: "#FF6B00", // Döner turuncusu
                secondary: "#1E293B",
                accent: "#F59E0B",
            }
        },
    },
    plugins: [],
}
