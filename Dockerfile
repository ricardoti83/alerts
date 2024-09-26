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

# Criar o arquivo de log para o cron
RUN touch /var/log/mycron.log

# Adicionar o script Python no cron para rodar a cada 6 horas
RUN echo "* * * * * /usr/local/bin/python3 /app/main.py >> /var/log/mycron.log 2>&1" > /etc/cron.d/azure-check-cron


# Dar permissões ao cron job
RUN chmod 0644 /etc/cron.d/azure-check-cron

# Criar a pasta de dados
RUN mkdir -p /data

# Aplicar cron job
RUN crontab /etc/cron.d/azure-check-cron

# Executa o cron e mantém o container rodando
CMD cron && tail -f /var/log/mycron.log
