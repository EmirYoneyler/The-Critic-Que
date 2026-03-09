/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Film eleştirisi temasına uygun özel renkler
        'lbx-green': '#00e054', // Letterboxd yeşili
        'lbx-orange': '#ff8000',
        'lbx-blue': '#40bcf4',
      },
    },
  },
  plugins: [],
}