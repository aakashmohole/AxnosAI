FROM node:20-alpine

WORKDIR /usr/src/app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy source code and build
COPY . .
RUN npm run build

# Expose NestJS port
EXPOSE 3001

# Start the server
CMD ["npm", "run", "start:prod"]
