# Pre-deployment steps

!!! info
    See [Environment variables](../environment-variables.md) for full details of the deployment related variables.

## Set environment configuration variables of shared management resources

1. Open the `/devops/.env.sample` file and then save it without the .sample extension. You should now have a file called `.env` located in the `/devops` folder. The file contains configuration variables for the shared management infrastructure which is used to support the deployment of one or more Azure TRE instances.

  You need to provide values for the following variables:

  | Variable | Description |
  | -------- | ----------- |
  | `LOCATION` | The [Azure location (region)](https://azure.microsoft.com/global-infrastructure/geographies/#geographies) for all resources. |
  | `MGMT_RESOURCE_GROUP_NAME` | The shared resource group for all management resources, including the storage account. |
  | `MGMT_STORAGE_ACCOUNT_NAME` | The name of the storage account to hold the Terraform state and other deployment artifacts. |
  | `ACR_NAME` | A globally unique name for the [Azure Container Registry (ACR)](https://docs.microsoft.com/azure/container-registry/) that will be created to store deployment images. |
  | `ARM_SUBSCRIPTION_ID` | The Azure subscription ID for all resources. |

  !!! tip
      To retrieve your Azure subscription ID, use the `az` command line interface available in the development container. In the terminal window in Visual Studio Code, type `az login` followed by `az account show` to see your default subscription. Please refer to `az account -help` for further details on how to change your active subscription.

2. Comment out the following variables by starting the line with a hash `#`.

  ```cmd
  # ARM_TENANT_ID=...
  # ARM_CLIENT_ID=...
  # ARM_CLIENT_SECRET=...
  ```

The rest of the variables can have their default values. You should now have a `.env` file that looks similar to the one below:

```plaintext
# Management infrastructure
LOCATION=westeurope
MGMT_RESOURCE_GROUP_NAME=aztremgmt
MGMT_STORAGE_ACCOUNT_NAME=aztremgmt
TERRAFORM_STATE_CONTAINER_NAME=tfstate
IMAGE_TAG=dev
ACR_NAME=aztreacr

ARM_SUBSCRIPTION_ID=12...54e

# Azure Resource Manager credentials used for CI/CD pipelines
# ARM_TENANT_ID=__CHANGE_ME__
# ARM_CLIENT_ID=__CHANGE_ME__
# ARM_CLIENT_SECRET=__CHANGE_ME__

PORTER_OUTPUT_CONTAINER_NAME=porterout

# Debug mode
DEBUG="false"
```

## Set environment configuration variables of the Azure TRE instance

Next, you will set the configuration variables for the specific Azure TRE instance:

1. Use the terminal window in Visual Studio Code to execute the following script from within the development container:

   ```bash
   /workspaces/tre> az login
   ```

  !!! note
      In case you have several subscriptions and would like to change your default subscription use `az account set --subscription <desired subscription ID>`

1. Open the `/templates/core/.env.sample` file and then save it without the .sample extension. You should now have a file called `.env` located in the `/templates/core` folder.
1. Set the first one of the variables, `TRE_ID`, which is the alphanumeric, with underscores and hyphens allowed, ID for the Azure TRE instance. The value will be used in various Azure resources, and **needs to be globally unique and less than 12 characters in length**. Use only lowercase letters. Choose wisely!
1. Run the `/scripts/aad-app-reg.sh` script to create API and Swagger UI app registrations and their service principals. The details of the script are covered [app registration script](../auth.md#app-registration-script) section of the auth document. Below is a sample where `TRE_ID` has value `mytre` and the Azure location is `westeurope`:

  ```bash
  /workspaces/tre> ./scripts/aad-app-reg.sh -n TRE -r https://mytre.westeurope.cloudapp.azure.com/oidc-redirect -a
  ```

  !!! note
      The full functionality of the script requires directory admin privileges. You may need to contact your friendly AAD admin to complete this step. The app registrations can be created manually in Azure Portal too. For more information, see [Authentication and authorization](../auth.md).


  With the output of the script, you can now provide the required auth related values for the following variables in the `/templates/core/.env` configuration file:

  | Variable | Description |
  | -------- | ----------- |
  | `AAD_TENANT_ID` | The Azure AD Tenant ID. |
  | `API_CLIENT_ID` | API application (client) ID. |
  | `API_CLIENT_SECRET` | API application client secret. |
  | `SWAGGER_UI_CLIENT_ID` | Swagger (OpenAPI) UI application (client) ID. |

All other variables can have their default values for now. You should now have a `.env` file that looks similar to below:

```plaintext
# Used for TRE deployment
TRE_ID=mytre
CORE_ADDRESS_SPACE="10.1.0.0/22"
TRE_ADDRESS_SPACE="10.0.0.0/12"
API_IMAGE_TAG=dev
RESOURCE_PROCESSOR_VMSS_PORTER_IMAGE_TAG=dev
GITEA_IMAGE_TAG=dev
DEPLOY_GITEA=true
RESOURCE_PROCESSOR_TYPE="vmss_porter"

# Auth configuration
AAD_TENANT_ID=72e...45
API_CLIENT_ID=af6...dc
API_CLIENT_SECRET=abc...12
SWAGGER_UI_CLIENT_ID=d87...12
```

## Add admin user

Make sure the **TRE Administrators** and **TRE Users** roles, defined by the API app registration, are assigned to your user and others as required. See [Enabling users](../auth.md#enabling-users) for instructions.

## Next steps

* [Deploying Azure TRE](deploying-azure-tre.md)
