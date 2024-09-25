# Usar uma imagem base do Python
FROM python:3.9-slim

# Instalar cron e dependências do sistema
RUN apt-get update && apt-get install -y cron && apt-get clean

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar os arquivos de requirements e o código para o contêiner
COPY requirements.txt requirements.txt
COPY . .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Adicionar o script Python no cron para rodar a cada 6 horas
RUN echo "0 */1 * * * python3 /app/main.py >> /var/log/mycron.log 2>&1" > /etc/cron.d/azure-check-cron

# Dar permissões ao cron job
RUN chmod 0644 /etc/cron.d/azure-check-cron

# Aplicar cron job
RUN crontab /etc/cron.d/azure-check-cron

# Iniciar o serviço cron no contêiner e também iniciar o servidor Flask
CMD cron && python /app/main.py
