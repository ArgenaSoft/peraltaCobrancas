FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Criar usuário sem privilégios
RUN addgroup -S app && adduser -S -G app app
RUN chown -R app:app /app
USER app

EXPOSE 3000
CMD ["node_modules/.bin/next", "start"]