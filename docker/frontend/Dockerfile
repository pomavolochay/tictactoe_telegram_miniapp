# syntax=docker/dockerfile:1.7
FROM node:20-alpine AS base
WORKDIR /app
ENV NODE_ENV=production
RUN corepack enable
COPY apps/frontend/package.json ./
RUN pnpm install --frozen-lockfile --prod=false || pnpm install --prod=false

FROM base AS dev
ENV NODE_ENV=development
COPY apps/frontend/ .
CMD ["pnpm", "dev"]

FROM base AS build
COPY apps/frontend/ .
RUN pnpm install --frozen-lockfile --prod=false || pnpm install --prod=false
RUN pnpm build

FROM node:20-alpine AS prod
WORKDIR /app
ENV NODE_ENV=production
RUN corepack enable
COPY --from=build /app/.output ./.output
EXPOSE 3000
HEALTHCHECK CMD node -e "fetch('http://localhost:3000/health').then(()=>process.exit(0)).catch(()=>process.exit(1))"
CMD ["node", ".output/server/index.mjs"]
