#!/bin/bash

# az cloud set --name AzureChinaCloud
az login

# subscription="bsh-cloud-connectivity-n3"
subscription=$1

# 列出Azure订阅中的所有vnet、子网、对等信息
az network vnet list --subscription ${subscription} | jq '.[] | {name: .name, addressPrefixes: .addressSpace[], subnets: [.subnets[].name], subnets_addr: [.subnets[].addressPrefix], peering: [.virtualNetworkPeerings[].name], peering_remote: [.virtualNetworkPeerings[].remoteVirtualNetwork.id], peering_remote_addr: [.virtualNetworkPeerings[].remoteVirtualNetworkAddressSpace.addressPrefixes]}'

