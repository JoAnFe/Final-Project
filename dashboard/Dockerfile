FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm i
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Serve on :5173 for compatibility with your compose mapping
EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]