# Etapa 1: build
FROM node:20-alpine AS builder

WORKDIR /app

# Copia os arquivos de dependência e instala dependências
COPY package.json package-lock.json ./
RUN npm ci

# Copia o restante do código e constrói o projeto
COPY . .
RUN npm run build

# Etapa 2: imagem final, leve, apenas com os arquivos necessários
FROM node:20-alpine AS runner

WORKDIR /app

# Define a variável de ambiente obrigatória para Next.js em produção
ENV NODE_ENV=production

# Copia somente o necessário para rodar o app
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Exponha a porta padrão do Next.js
EXPOSE 3000

# Comando para iniciar o servidor Next.js
CMD ["node_modules/.bin/next", "start"]

