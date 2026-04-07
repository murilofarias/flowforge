/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#fdfaf4",
        ink: "#2a2a33",
        trigger: { 50: "#e8f7ef", 500: "#34a86b", 700: "#1f7a4a" },
        action: { 50: "#e6f0ff", 500: "#3b7bdb", 700: "#2457a6" },
        transform: { 50: "#f1eafc", 500: "#8a63d2", 700: "#5f3fa8" },
        logic: { 50: "#fdf3dc", 500: "#d9a13a", 700: "#a5741c" },
        ai: { 50: "#ffe9f3", 500: "#d85590", 700: "#a7316a" },
      },
      boxShadow: {
        card: "0 1px 2px rgba(40,38,60,.04), 0 6px 20px rgba(40,38,60,.06)",
        pop: "0 10px 35px rgba(40,38,60,.12)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        mono: ["JetBrains Mono", "ui-monospace"],
      },
    },
  },
  plugins: [],
};
