FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG REACT_APP_API_BASE_URL
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL

RUN npm run build

# Install serve
RUN npm install -g serve

# Expose and run on port 8080
EXPOSE 8080
CMD ["serve", "-s", "build", "-l", "8080"]
