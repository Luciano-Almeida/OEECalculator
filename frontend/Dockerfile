# Usar a imagem base do Node.js
#FROM node:18
#FROM node:23.0.0-bullseye
FROM node:22.14.0-bullseye-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo package.json e instala as dependências
COPY package.json ./
RUN npm install --legacy-peer-deps

# Copia o restante do projeto para o container
COPY . .

# Expor a porta 3000
EXPOSE 3000

# Comando para rodar o React
#CMD ["npm", "start"]
CMD ["npm", "run", "dev", "--reload"]
