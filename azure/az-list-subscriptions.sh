#!/bin/bash

# az cloud set --name AzureChinaCloud
az login

# 列出Azure中的所有订阅
accounts=$(az account list | jq '.[].name')
IFS=$'\n' read -d '' -ra account_array <<< "$accounts"

# 去除首尾引号
for acc in "${account_array[@]}":
do
	if [ ${#acc} -gt 2 ]; then
		acc=${acc:1}
		acc=${acc%?}
	fi
	echo "$acc"
done

