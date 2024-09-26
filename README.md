## Criar um Service Principal na Azure

```
az ad sp create-for-rbac --name "AzureTagChecker" --role "Reader" --scopes "/subscriptions/{subscription-id}"
```

O comando deverá retornar a seguinte saída:

```
{
    "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "displayName": "AzureTagChecker",
    "password": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```
