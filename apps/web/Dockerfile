FROM node:22-alpine AS build
WORKDIR /repo
COPY package*.json ./
COPY apps/web/package.json apps/web/package.json
RUN npm ci
COPY apps/web apps/web
COPY content content
ARG NEXT_PUBLIC_SITE_URL=https://socialviddownloader.com
ARG ENABLE_HSTS=0
ENV NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL ENABLE_HSTS=$ENABLE_HSTS
RUN npm run build --workspace apps/web -- --webpack
FROM node:22-alpine
ENV NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000
WORKDIR /repo
COPY --from=build /repo/apps/web/.next/standalone ./
COPY --from=build /repo/apps/web/.next/static ./apps/web/.next/static
COPY --from=build /repo/apps/web/public ./apps/web/public
USER node
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
