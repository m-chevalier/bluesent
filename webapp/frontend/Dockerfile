FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies early for better caching
COPY package*.json ./
COPY prisma ./prisma
RUN npm ci

# Generate Prisma client
RUN npx prisma generate

# Copy the rest of the application code
COPY . .

# Build the Next.js app
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "run", "start"]
