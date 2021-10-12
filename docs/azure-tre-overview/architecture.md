# Azure TRE Architecture

The Azure Trusted Research Environment (TRE) consists of multiple components, all encapsulated in networks with restricted ingress- & egress traffic.

There is one network for the management components and one network per Workspace.

All traffic has to be explicitly allowed by the Application Gateway or the Firewall.

![Architecture overview](../assets/archtecture-overview.png)

The Azure TRE management plane consists of two groups of components:

- API & Composition Service
- Shared Services

!!! todo
    Shared Services is still work in progress. Please see [#23](https://github.com/microsoft/AzureTRE/issues/23), [#22](https://github.com/microsoft/AzureTRE/issues/21), & [#21](https://github.com/microsoft/AzureTRE/issues/21)

The TRE API is a service that users can interact with to request changes to workspaces e.g., to create, update, delete workspaces and workspace services inside each workspace. The Composition Service is doing the actual work of mutating the state of each Workspace including the Workspace Services.

Ingress/egress components governs all inbound and outbound traffic from the public Internet to and from Azure TRE including the Workspaces. The Firewall Service is managing the egress rules of the Firewall.

Shared Services are services available to all Workspaces. **Source Mirror** can mirror source repositories such as GitHub, but only allowing read-access, hence data from a Workspace cannot be pushed to a source repository.
**Package Mirror** is also a read-only front for developer/researcher application package services like NPM, PyPI, and NuGet and operating system application package services like apt-get and Windows Package Manager (winget).

## Composition Service

The Composition Service is responsible for managing and mutating Workspaces and Workspace Services.

A Workspace is an instance of a Workspace Template. A Workspace Template is implemented as a [Porter](https://porter.sh/) bundle - read more about [Authoring workspaces templates](../tre-workspace-authors/authoring-workspace-templates.md).

A Porter bundle is a fully encapsulated versioned bundle with everything needed (binaries, scripts, IoC templates etc.) to provision an instance of Workspace Template.

The [TRE Administrator](user-roles.md#tre-administrator) can register a Porter bundle to use the Composition Service to provision instances of the Workspace Templates.

This requires:

1. The Porter bundle to be pushed to the Azure Container Registry (ACR).
1. Registering the Workspace through the API.

Details on how to [register a Workspace Template](../tre-workspace-authors/registering-workspace-templates.md).

The Composition Service consists of multiple components.

| Component Name | Responsibility / Description |
| --- | --- |
| TRE API | An API responsible for performing all operations on Workspaces and managing Workspace Templates. |
| Configuration Store | Keeping the state of Workspaces and Workspace Templates. The store uses [Cosmos DB (SQL)](https://docs.microsoft.com/en-us/azure/cosmos-db/introduction). |
| Service Bus | [Azure Service Bus](https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview) responsible for reliable delivery of messages between components.  |
| Resource Processor | Responsible for starting the process of mutating a Workspace via a Workspace Template. |

## Provisioning a Workspace

![Composition Service](../assets/composition-service.png)

The flow to provision a Workspace is as follows (the flow is the same for all kinds of mutations to a Workspace):

1. TRE Admin sends an HTTP request to the TRE API to create a new Workspace. The request contains information like the name of the Workspace, the Workspace Template to use, and the parameters required for the Workspace Template (Workspace Templates can expose the parameters via a JSON Schema ).
1. The API saves the desired state of the Workspace in the Configuration Store.
1. The API sends a command message with the Workspace Template reference and parameters to the `workspacequeue`.

    ```JSON
    {
            "action": "install",
            "id": "base",
            "name": "BaseWorkspaceTemplate",
            "version": "1.0",
            "parameters": {
                "param1": "value1"
            }
        }
    ```

1. The Resource Processor picks up the new message from the service bus queue.
1. The Resource Processor processes the command by executing the Porter bundle (the implementation of a Workspace Template).

    ```bash
    # simplified for readability
    porter <action> --reference <ACR name>.azurecr.io/bundles/<name>:<version> --params key=value --cred <credentials set name or file>

    # Example
    porter install --reference msfttreacr.azurecr.io/bundles/BaseWorkspaceTemplate:1.0 --params param1=value1 --cred azure.json
    ```

    Deployments are carried out against the Azure Subscription using a User Assigned Managed Identity. The `azure.json` tells Porter where the credential information can be found and for the Resource Processor they are set as environment variables.

    Porter bundle actions are required to be idempotent, so if a deployment fails, the Resource Processor can retry.

1. The Porter Docker bundle is pulled from the Azure Container Registry (ACR) and executed.
1. The Porter bundle executes against Azure Resource Manager to provision Azure resources. Any kind of infrastructure of code frameworks like ARM, Terraform, or Pulumi can be used or scripted via PowerShell or Azure CLI.
1. Porter stores state and outputs in Azure Storage Containers. State for keeping persistent state between executions of a bundled with the same Workspace.
1. For the time being, the Porter bundle updates Firewall rules directly setting egress rules. An enhancement to implement a Shared Firewall services is planned ([#23](https://github.com/microsoft/AzureTRE/issues/23)).
1. The Resource Processor sends events to the `deploymentstatus` queue on state changes and informs if the deployment succeeded or failed.
1. The API receives the status of the Porter bundle execution.
1. The API updates the status of the Porter bundle execution in the Configuration Store.

!!! info
    The Resource Processor is a Docker container running on a Linux VM scale set.

!!! todo
    Currently, the bundle keeps state between executions in a Storage Container (TF state) passed in a parameters to the bundle. An enhancement issues [#536](https://github.com/microsoft/AzureTRE/issues/536) exists to configure Porter state management.
