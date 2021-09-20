# Azure ML and Dev Test Labs Workspace

This deploys a TRE workspace with the following services:

- [Azure ML](../../../templates/workspace_services/azureml)
- [Azure Dev Test Labs](../../../templates/workspace_services/devtestlabs)

Please follow the above links to learn more about how to access the services and any firewall rules that they will open in the workspace.

## Manual deployment

1. Publish the bundles required for this workspace:

  *Base Workspace*
  
  ```cmd
  make porter-build DIR=./templates/workspaces/base
  make porter-publish DIR=./templates/workspaces/base
  ```

  *Azure ML Service*

  ```cmd
  make porter-build DIR=./templates/workspace_services/azureml
  make porter-publish DIR=./templates/workspace_services/azureml
  ```

  *DevTest Labs Service*

  ```cmd
  make porter-build DIR=./templates/workspace_services/devtestlabs
  make porter-publish DIR=./templates/workspace_services/devtestlabs
  ```

1. Create a copy of `workspaces/azureml_devtestlabs/.env.sample` with the name `.env` and update the variables with the appropriate values.

  | Environment variable name | Description |
  | ------------------------- | ----------- |
  | `WORKSPACE_ID` | A 4 character unique identifier for the workspace for this TRE. `WORKSPACE_ID` can be found in the resource names of the workspace resources; for example, a `WORKSPACE_ID` of `ab12` will result in a resource group name for workspace of `rg-<tre-id>-ab12`. Allowed characters: Alphanumeric. |
  | `ADDRESS_SPACE` | The address space for the workspace virtual network. For example `192.168.1.0/24`|

1. Build and install the workspace:

  ```cmd
  make porter-build DIR=./templates/workspaces/azureml_devtestlabs
  make porter-publish DIR=./templates/workspaces/azureml_devtestlabs
  make porter-install DIR=./templates/workspaces/azureml_devtestlabs
  ```
