#!/bin/bash

if [ DEPLOY_NEXUS==true ] 
then
  echo -e "\e[33m»»» Nexus deployment not enabled (DEPLOY_NEXUS not true); exiting"
  exit
fi

export NEXUS_URL="${TRE_URL}/nexus/"
export NEXUS_ADMIN_PASSWORD_NAME="nexus-${TRE_ID,,}-admin-password"
export KEYVAULT_NAME="kv-${TRE_ID}"
export STORAGE_ACCOUNT_NAME="stg${TRE_ID//-/}"

export NEXUS_PASS=$(az keyvault secret show --name ${NEXUS_ADMIN_PASSWORD_NAME} --vault-name ${KEYVAULT_NAME} -o json | jq -r '.value')

if [ -z "$NEXUS_PASS" ]; then
    # The pass couldn't be found in Key Vault, fetching from nexus_data
    while [ $(az storage file exists -p admin.password -s nexus-data --account-name ${STORAGE_ACCOUNT_NAME,,} -o json | jq '.exists')==false ]; do
        echo "Waiting for admin pass..."
        sleep 10
    done

    # The initial password file exists, let's get it 
    az storage file download -p admin.password -s nexus-data --account-name ${STORAGE_ACCOUNT_NAME,,}
    export NEXUS_PASS=`cat admin.password`

    #we have the initial password; let's try to connect to Nexus and reset the password
    export NEW_PASSWORD=$(date +%s | sha256sum | base64 | head -c 32 ; echo)

    curl -ifu admin:$NEXUS_PASS \
         -XPUT -H 'Content-Type: text/plain' \
         --data "${NEW_PASSWORD}" \
        $NEXUS_URL/service/rest/v1/security/users/admin/change-password

    #Let's store the new pass into Key Vault
    az keyvault secret set --name ${NEXUS_ADMIN_PASSWORD_NAME} --vault-name ${KEYVAULT_NAME}--value $NEW_PASSWORD
    export NEXUS_PASS=$NEW_PASSWORD
fi

#Check if the repo already exists
export STATUS_CODE=$(curl -iu admin:$NEXUS_PASS -X "GET" "${NEXUS_URL}/service/rest/v1/repositories/apt/proxy/pypi-proxy-repo" -H "accept: application/json" -k -s -w "%{http_code}" -o /dev/null)

if [[ ${STATUS_CODE} == 404 ]] 
 then
    # Let's create pypi proxy
    curl -iu admin:$NEXUS_PASS -XPOST \
    $NEXUS_URL/service/rest/v1/repositories/apt/proxy \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '@pypi_proxy_conf.json'
fi
