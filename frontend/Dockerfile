# Etap 1: Instalacja zależności (deps)
# Używamy node:20-slim (oparty na Debianie) zamiast Alpine,
# aby mieć dostęp do 'bash' i standardowych narzędzi systemowych.
FROM node:20-slim as deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

# Etap 2: Budowanie aplikacji (builder)
FROM node:20-slim as builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Etap 3: Finalny obraz produkcyjny/Dev Runtime
FROM node:20-slim
WORKDIR /app
# W trybie dev, Next.js uruchamia się inaczej, ale Dockerfile jest potrzebny
COPY package.json package-lock.json ./
RUN npm install --only=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
CMD ["npm", "start"]
