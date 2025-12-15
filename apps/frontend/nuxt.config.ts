import { defineNuxtConfig } from "nuxt/config";

export default defineNuxtConfig({
  ssr: false,

  devtools: { enabled: true },

  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt"],

  css: ["~/assets/css/tailwind.css"],

  runtimeConfig: {
    public: {
      // IMPORTANT:
      // - In Telegram Mini App you must serve over HTTPS.
      // - Prefer relative /api when frontend + backend are behind the same domain + ingress.
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "/api",
    },
  },

  app: {
    head: {
      title: "Уютный TicTacToe",
      meta: [
        { charset: "utf-8" },
        // Telegram WebApp prefers no zoom and correct safe-area/viewport handling
        {
          name: "viewport",
          content:
            "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover",
        },
        { name: "theme-color", content: "#fdf7f2" },
      ],
      link: [
        { rel: "preconnect", href: "https://fonts.googleapis.com" },
        {
          rel: "preconnect",
          href: "https://fonts.gstatic.com",
          crossorigin: "",
        },
        {
          rel: "stylesheet",
          href: "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Merriweather:wght@400;500;600&display=swap",
        },
      ],
    },
  },

  tailwindcss: {
    viewer: false,
  },

  typescript: {
    strict: true,
    typeCheck: true,
  },

  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },
});
