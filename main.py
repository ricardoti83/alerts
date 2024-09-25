import os
import csv
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

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

if __name__ == "__main__":
    alert_resources_without_tags()
