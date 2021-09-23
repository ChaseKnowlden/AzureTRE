# InnerEye Service Bundle

See: [https://github.com/microsoft/InnerEye-DeepLearning](https://github.com/microsoft/InnerEye-DeepLearning)

## Firewall Rules

Please be aware that the following Firewall rules are opened for the workspace when this service is deployed. These are all dependencies needed by InnerEye to be able to develop and train models:

URLs:

- *.anaconda.com
- *.anaconda.org
- binstar-cio-packages-prod.s3.amazonaws.com
- github.com
- *pypi.org
- *pythonhosted.org
- github-cloud.githubusercontent.com

## Prerequisites

- [A workspace with an Azure ML Service bundle installed](../../../templates/workspace_services/azureml)

## Manual Deployment

1. Create a copy of `templates/workspace_services/innereye/.env.sample` with the name `.env` and update the variables with the appropriate values.

  | Environment variable name | Description |
  | ------------------------- | ----------- |
  | `WORKSPACE_ID` | The 4 character unique identifier used when deploying the base workspace bundle. |
  | `AZUREML_WORKSPACE_NAME` | Name of the Azure ML workspace deployed as part of the Azure ML workspace service prerequisite. |
  | `AZUREML_ACR_ID` | Azure resource ID of the Azure Container Registry deployed as part of the Azure ML workspace service prerequisite. |

1. Build and install the InnerEye Deep Learning Service bundle

  ```cmd
  make porter-build DIR=./templates/workspace_services/innereye
  make porter-publish DIR=./templates/workspace_services/innereye
  make porter-install DIR=./templates/workspace_services/innereye
  ```

## Running the InnerEye HelloWorld on AML Compute Cluster

1. Log onto a VM in the workspace, open PowerShell and run:

  ```cmd
  git clone https://github.com/microsoft/InnerEye-DeepLearning
  cd InnerEye-DeepLearning
  git lfs install
  git lfs pull
  conda init
  conda env create --file environment.yml
  ```

1. Restart PowerShell and navigate to the "InnerEye-DeepLearning" folder

  ```cmd
  conda activate InnerEye
  ```

1. Open Azure Storage Explorer and connect to your Storage Account using name and access key
1. On the storage account create a container with name ```datasets``` and a folder named ```hello_world```
1. Copy `dataset.csv` file from `Tests/ML/test_data/dataset.csv` to the `hello_world` folder
1. Copy the whole `train_and_test_data` folder from `Test/ML/test_data/train_and_test_data` to the `hello_world` folder
1. Update the following variables in `InnerEye/settings.yml`: subscription_id, resource_group, workspace_name, cluster (see [AML setup](https://github.com/microsoft/InnerEye-DeepLearning/blob/main/docs/setting_up_aml.md) for more details).
1. Open your browser to ml.azure.com, login, select the right Subscription and AML workspace and then navigate to `Data stores`. Create a New datastore named `innereyedatasets` and link it to your storage account and datasets container.
1. Back from PowerShell run

   ```cmd
   python InnerEye/ML/runner.py --model=HelloWorld --azureml=True
   ```

1. The runner will provide you with a link and ask you to open it to login. Copy the link and open it in browser (Edge) on the DSVM and login. The run will continue after login.
1. In your browser navigate to ml.azure.com and open the `Experiments` tab to follow the progress of the training


## Configuring and testing inference service

The workspace service provision an App Service Plan and an App Service for hosting the inference webapp. The webapp will be integrated into the workspace network, allowing the webapp to connect to the AML workspace. Following the setup you will need to:

1. Log onto a VM in the workspace and run:

  ```cmd
  git clone https://github.com/microsoft/InnerEye-Inference
  cd InnerEye-Inference
  az webapp up --name <inference-app-name> -g <resource-group-name>
  ```

1. Create a new container in your storage account for storing inference images called `inferencedatastore`.
1. Create a new folder in that container called `imagedata`.
1. Navigate to the ml.azure.com, `Datastores` and create a new datastore named `inferencedatastore` and connect it to the newly created container.
1. The key used for authentication is the `inference_auth_key` provided as an output of the service deployment.
1. Test the service by sending a GET or POST command using curl or Invoke-WebRequest:

   Simple ping:

    ```cmd
    Invoke-WebRequest https://yourservicename.azurewebsites.net/v1/ping -Headers @{'Accept' = 'application/json'; 'API_AUTH_SECRET' = 'your-secret-1234-1123445'}
    ```

    Test connection with AML:
  
    ```cmd
    Invoke-WebRequest https://yourservicename.azurewebsites.net/v1/model/start/HelloWorld:1 -Method POST -Headers @{'Accept' = 'application/json'; 'API_AUTH_SECRET' = 'your-secret-1234-1123445'}
    ```
