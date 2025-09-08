/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.7s cubic-bezier(0.4,0,0.2,1) forwards',
      },
      colors: {
        primary: "#007bff",
        secondary: "#6c757d",
        warning: "#ffc107",
        success: "#28a745",
        muted: "#6c757d",
        foreground: "#f8f9fa",
        "primary-foreground": "#fff",
        "muted-foreground": "#adb5bd",
        border: "#dee2e6",
        "tertiary": "#6610f2",
        // Custom colors for simulation topics
        "yellow-400": "#FFD600",
        "orange-500": "#FF6B00",
        "green-400": "#38A169",
        "blue-500": "#00529B",
        "purple-400": "#A259FF",
        "pink-500": "#FF2D55",
        // Tambahkan warna lain sesuai kebutuhan
      },
      boxShadow: {
        card: "0 4px 24px rgba(0,0,0,0.08)",
        float: "0 8px 32px rgba(0,0,0,0.12)",
        glow: "0 0 16px #007bff55",
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(90deg, #007bff 0%, #6610f2 100%)',
        'gradient-glass': 'linear-gradient(135deg, #f8f9fa 0%, #dee2e6 100%)',
        // Custom gradients for topic cards
        'gradient-to-r-yellow-orange': 'linear-gradient(to right, #FFD600, #FF6B00)',
        'gradient-to-r-green-blue': 'linear-gradient(to right, #38A169, #00529B)',
        'gradient-to-r-purple-pink': 'linear-gradient(to right, #A259FF, #FF2D55)',
      },
      fontFamily: {
        inter: ["Inter", "sans-serif"],
      },
      transitionProperty: {
        bounce: "transform, box-shadow",
      },
    },
  },
  plugins: [],
}
