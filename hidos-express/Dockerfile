FROM node:24-alpine
ENV NODE_ENV=production PORT=3000
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY app.js index.html ./
COPY public ./public
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s CMD wget -q -O /dev/null http://127.0.0.1:3000/ || exit 1
CMD ["node", "app.js"]
