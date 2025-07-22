# Use official Bun runtime as base image
FROM oven/bun:1-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json bun.lock* ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN bun run build

# Expose port 5173 (Vite's default dev port)
EXPOSE 5173

# Start the application in preview mode (serves built files)
CMD ["bun", "run", "preview", "--host", "0.0.0.0", "--port", "5173"]
