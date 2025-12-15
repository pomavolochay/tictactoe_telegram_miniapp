import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './composables/**/*.{js,ts}',
    './plugins/**/*.{js,ts}',
    './app.vue'
  ],
  theme: {
    extend: {
      colors: {
        shell: '#fdf7f2',
        petal: '#ffe4ec',
        lilac: '#e7defa',
        mist: '#e9f5f2',
        sage: '#9eb6a8',
        cocoa: '#4b3c47',
        coral: '#f9c6bd',
        plum: '#7a5c8e'
      },
      fontFamily: {
        sans: ['\'Manrope\'', 'sans-serif'],
        serif: ['\'Merriweather\'', 'serif']
      }
    }
  }
}
