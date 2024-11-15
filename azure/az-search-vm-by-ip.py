from azure.identity import AzureCliCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from msrestazure.azure_cloud import AZURE_CHINA_CLOUD as cloud_env

# 初始化凭据和客户端
subscription_id = ""
credential = AzureCliCredential()

network_client = NetworkManagementClient(
    credential=credential,
    base_url=cloud_env.endpoints.resource_manager,
    credential_scopes=[cloud_env.endpoints.resource_manager + "/.default"],
    subscription_id=subscription_id
)
compute_client = ComputeManagementClient(
    credential=credential,
    base_url=cloud_env.endpoints.resource_manager,
    credential_scopes=[cloud_env.endpoints.resource_manager + "/.default"],
    subscription_id=subscription_id
)

def get_vm_info_by_ip(ip_address):
    # 根据IP地址查找对应的网络接口
    for nic in network_client.network_interfaces.list_all():
        for ip_config in nic.ip_configurations:
            if (ip_config.private_ip_address == ip_address) or (ip_config.public_ip_address and ip_config.public_ip_address.ip_address == ip_address):
                # 找到IP地址对应的虚拟机资源ID
                vm_id = nic.virtual_machine.id if nic.virtual_machine else None
                if vm_id:
                    # 获取虚拟机信息
                    vm = compute_client.virtual_machines.get(
                        resource_group_name=vm_id.split("/")[4],
                        vm_name=vm_id.split("/")[-1]
                    )
                    return {
                        "vm_name": vm.name,
                        "location": vm.location,
                        "os_type": vm.storage_profile.os_disk.os_type,
                        "vm_size": vm.hardware_profile.vm_size,
                        "network_interfaces": [iface.id for iface in vm.network_profile.network_interfaces],
                        "service_tag": vm.tags
                    }
    return None

# 使用例子
ip_address = "10.20.141.70"
vm_info = get_vm_info_by_ip(ip_address)

if vm_info:
    print(vm_info["service_tag"]["ServiceOwner"])
else:
    print("未找到对应的虚拟机。")

