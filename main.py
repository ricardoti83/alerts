import os
import csv
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')

def send_email_with_csv(csv_file_path):
    fromaddr = "contato@cloudwings.com.br"
    toaddr = "ricardofromit@gmail.com"
    msg = MIMEMultipart()

    # Configurações do e-mail
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Relatório de Recursos Sem Tags"

    # Corpo do e-mail
    body = "Segue em anexo o relatório de recursos sem tags na assinatura."

    msg.attach(MIMEText(body, 'plain'))

    # Anexar o arquivo CSV
    filename = os.path.basename(csv_file_path)
    attachment = open(csv_file_path, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {filename}")
    msg.attach(part)

    # Configurações do servidor SMTP (por exemplo, Gmail)
    server = smtplib.SMTP('smtp.umbler.com', 587)
    server.starttls()
    server.login(fromaddr, "Fl0ki1983@!")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

# Exemplo de uso
csv_file_path = '/app/data/resources_without_tags.csv'
send_email_with_csv(csv_file_path)

# Função para obter todas as assinaturas associadas ao Service Principal
def get_all_subscriptions():
    """Obtém todas as assinaturas da conta Azure usando as credenciais do Service Principal."""
    credential = DefaultAzureCredential()
    subscription_client = SubscriptionClient(credential)
    subscriptions = subscription_client.subscriptions.list()
    return [sub.subscription_id for sub in subscriptions]

# Função para listar recursos sem tags dentro de uma assinatura específica
def list_resources_without_tags(subscription_id, credential):
    """Lista todos os recursos sem tags em uma assinatura."""
    resource_client = ResourceManagementClient(credential, subscription_id)
    resources_without_tags = []

    # Listar todos os recursos da assinatura
    for resource in resource_client.resources.list():
        if not resource.tags:  # Verifica se o recurso não tem tags
            resources_without_tags.append(resource)

    return resources_without_tags

# Função para salvar os resultados em um arquivo CSV
def save_results_to_csv(results, output_file):
    """Salva os resultados em um arquivo CSV."""
    keys = results[0].keys() if results else []
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

# Função principal para percorrer todas as assinaturas e verificar os recursos sem tags
def alert_resources_without_tags():
    """Verifica todos os recursos sem tags em todas as assinaturas e salva os resultados."""
    credential = DefaultAzureCredential()
    subscription_ids = get_all_subscriptions()

    all_results = []
    
    # Loop para percorrer todas as assinaturas
    for subscription_id in subscription_ids:
        print(f"\nVerificando recursos sem tags na assinatura: {subscription_id}")
        resources_without_tags = list_resources_without_tags(subscription_id, credential)
        
        for resource in resources_without_tags:
            result = {
                "subscription_id": subscription_id,
                "resource_name": resource.name,
                "resource_type": resource.type,
                "resource_location": resource.location
            }
            all_results.append(result)
    
    # Definir o caminho para salvar o arquivo CSV fora do container
    output_path = '/data/resources_without_tags.csv'
    save_results_to_csv(all_results, output_path)
    print(f"Resultados salvos em {output_path}")

    send_email_with_csv(csv_file_path)
    print(f"Enviando o email")

if __name__ == "__main__":
    alert_resources_without_tags()
    
