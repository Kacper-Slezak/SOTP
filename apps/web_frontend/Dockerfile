# Stage 1: Dependency installation
FROM node:20-slim as deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install


# Stage 2: Application build
FROM node:20-slim as builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Final production image
FROM node:20-slim
WORKDIR /app
# Production container entrypoint
COPY package.json package-lock.json ./
RUN npm install --only=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
CMD ["npm", "start"]
