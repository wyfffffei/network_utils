from azure.identity import AzureCliCredential
from azure.mgmt.resource import SubscriptionClient
from msrestazure.azure_cloud import AZURE_CHINA_CLOUD as cloud_env

credential = AzureCliCredential()
subscription_client = SubscriptionClient(
    credential=credential,
    base_url=cloud_env.endpoints.resource_manager,
    credential_scopes=[cloud_env.endpoints.resource_manager + "/.default"],
)

def list_all_subscriptions():
    subscriptions = []
    for sub in subscription_client.subscriptions.list():
        subscriptions.append({
            "subscription_id": sub.subscription_id,
            "subscription_name": sub.display_name
        })
    return subscriptions

SUB = list_all_subscriptions()
for item in SUB:
    print(item["subscription_id"])

