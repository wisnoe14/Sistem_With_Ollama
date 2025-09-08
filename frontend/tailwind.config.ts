import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // Mencakup semua file di dalam folder src
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

export default config