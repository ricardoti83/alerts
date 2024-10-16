import os
import json
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
            # Adiciona a data de criação do recurso, se disponível
            creation_date = resource.created_time if hasattr(resource, 'created_time') else 'N/A'
            resources_without_tags.append({
                "resource_name": resource.name,
                "resource_type": resource.type,
                "resource_location": resource.location,
                "subscription_id": subscription_id,
                "creation_date": creation_date
            })

    return resources_without_tags

# Função para salvar os resultados em um arquivo JSON
def save_results_to_json(results, output_file):
    """Salva os resultados em um arquivo JSON, incluindo a contagem total de recursos."""
    
    # Adicionar a contagem total de recursos ao final dos resultados
    total_resources = len(results)
    results.append({"total_resources": total_resources})
    
    # Escrever os resultados no arquivo JSON
    with open(output_file, 'w') as jsonfile:
        json.dump(results, jsonfile, indent=4)

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
        all_results.extend(resources_without_tags)

    # Definir o caminho para salvar o arquivo JSON
    output_path = '/data/resources_without_tags.json'
    save_results_to_json(all_results, output_path)
    print(f"Resultados salvos em {output_path}")

if __name__ == "__main__":
    alert_resources_without_tags()
