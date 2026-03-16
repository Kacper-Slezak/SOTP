# Etap 1: Instalacja zależności
FROM node:20-slim as deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install


# Etap 2: Budowanie aplikacji
FROM node:20-slim as builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Etap 3: Finalny obraz produkcyjny (dla dev będzie inaczej)
FROM node:20-slim
WORKDIR /app
# W trybie dev, Next.js uruchamia się inaczej, ale Dockerfile jest potrzebny
COPY package.json package-lock.json ./
RUN npm install --only=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
CMD ["npm", "start"]
