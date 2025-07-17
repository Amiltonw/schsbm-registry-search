# Deployment Strategy for Django Application on Azure with Continuous Deployment

This document outlines the strategy for maintaining separate development and production environments for a Django application and deploying it to Azure using Continuous Deployment (CD) via GitHub Actions.

## 1. Environment Separation (Django Settings)

The core of this strategy is to separate Django settings into environment-specific files.

*   **`nrn_search/settings/` directory**: A new directory will be created to house all settings files.
*   **`nrn_search/settings/base.py`**: This file will contain all common settings that apply to both development and production environments (e.g., `INSTALLED_APPS`, `MIDDLEWARE`, `TEMPLATES`, `STATIC_URL`, etc.).
*   **`nrn_search/settings/dev.py`**: This file will contain settings specific to the local development environment.
    *   It will import all settings from `base.py` (`from .base import *`).
    *   `DEBUG` will be set to `True`.
    *   `ALLOWED_HOSTS` will be empty or set to `['localhost', '127.0.0.1']`.
    *   Database configuration will point to a local database (e.g., SQLite or local PostgreSQL).
    *   Development-specific `INSTALLED_APPS` (e.g., `debug_toolbar`) can be added here.
*   **`nrn_search/settings/prod.py`**: This file will contain settings specific to the production environment on Azure.
    *   It will import all settings from `base.py` (`from .base import *`).
    *   `DEBUG` will be set to `False`.
    *   `ALLOWED_HOSTS` will be dynamically loaded from an environment variable provided by Azure (e.g., `os.environ.get('ALLOWED_HOSTS').split(',')`).
    *   `SECRET_KEY` will be loaded from an environment variable provided by Azure (`os.environ.get('SECRET_KEY')`).
    *   Database configuration (`DATABASES`) will use environment variables to connect to Azure Database for PostgreSQL.
    *   `STATIC_ROOT` will be defined to specify where static files are collected for serving in production.

## 2. Dynamic Settings Loading (WSGI/ASGI and manage.py)

The `wsgi.py` and `asgi.py` (if applicable) files will be modified to dynamically load the correct settings file based on an environment variable (`DJANGO_SETTINGS_MODULE`). The `manage.py` script will also be updated to load environment variables from a local `.env` file for development.

*   **`DJANGO_SETTINGS_MODULE`**: This environment variable will dictate which settings file (`dev.py` or `prod.py`) Django should use.
    *   Locally, it will default to `nrn_search.settings.dev`.
    *   On Azure, it will be explicitly set to `nrn_search.settings.prod` via App Service Application Settings.
*   **`.env` file**: A `.env` file will be created in the project root for local development. This file will store local environment variables (e.g., local database credentials, development `SECRET_KEY`). **This file MUST be added to `.gitignore` to prevent it from being committed to version control.**

## 3. Azure Deployment with Continuous Deployment (GitHub Actions)

The deployment to Azure will leverage GitHub Actions for Continuous Deployment.

*   **Source Control**: The entire project, including the `Dockerfile` and the refactored settings, will be pushed to a GitHub repository.
*   **Azure App Service (Web App for Containers)**:
    *   An Azure App Service will be created, configured as a "Web App for Containers" on Linux.
    *   Continuous Deployment will be enabled from the GitHub repository. Azure will automatically generate a GitHub Actions workflow.
*   **GitHub Actions Workflow**: This workflow will automate the deployment process:
    *   **Trigger**: It will be triggered on pushes to the designated branch (e.g., `main`).
    *   **Build**: It will bprovuild the Docker image based on the `Dockerfile` in the repository.
    *   **Push**: The built Docker image will be pushed to an Azure Container Registry (ACR), which Azure will automatically set up.
    *   **Deploy**: The new image will be deployed to the Azure App Service.
*   **Azure App Service Application Settings**: Critical production environment variables (e.g., `DJANGO_SETTINGS_MODULE=nrn_search.settings.prod`, `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `ALLOWED_HOSTS`) will be configured directly in the Azure App Service's "Application settings". These are securely passed to the running container.
*   **Azure Database for PostgreSQL**: A separate Azure Database for PostgreSQL Flexible Server will be provisioned and configured to be accessible by the Azure App Service.

## 4. Post-Deployment Steps on Azure

After the initial deployment via CD:

*   **Database Migrations**: Connect to the App Service's SSH console and run `python manage.py migrate` to apply database migrations.
*   **Create Superuser**: Create an administrative user by running `python manage.py createsuperuser` via the App Service's SSH console.
*   **Collect Static Files**: While `STATIC_ROOT` is configured, Azure App Service for containers typically handles serving static files from the container. However, if you need to serve them via a CDN or Azure Storage, additional configuration would be required. For basic serving from the container, `collectstatic` ensures they are present in the image.

This strategy ensures a robust, secure, and automated deployment pipeline while maintaining a flexible development environment.
. Push Your Code to GitHub:
       * Ensure all the changes we've made (including the nrn_search/settings/ directory, updated manage.py, wsgi.py, asgi.py, Dockerfile,
         requirements.txt, and .gitignore) are committed and pushed to a GitHub repository. This repository will be the source for your
         Continuous Deployment.


   2. Azure Setup (via Azure Portal or Azure CLI):
       * Create a Resource Group: A logical container for your Azure resources.
       * Create Azure Database for PostgreSQL - Flexible Server: This will be your production database. Remember to configure firewall rules to
         allow connections from Azure services.
       * Create Azure App Service (Web App for Containers): This will host your Django application. When creating it, select "Docker Container"
         as the publish method and "Linux" as the operating system.


   3. Configure Continuous Deployment in Azure:
       * In the Azure Portal, navigate to your newly created App Service.
       * Go to the "Deployment Center".
       * Select "GitHub" as your source control provider.
       * Authorize Azure to access your GitHub account.
       * Choose your specific repository and the branch (e.g., main or master) that you want to deploy from.
       * Azure will detect your Dockerfile and automatically set up a GitHub Actions workflow. This workflow will handle building your Docker
         image, pushing it to an Azure Container Registry (ACR), and deploying it to your App Service whenever you push changes to your selected
         branch.


   4. Configure Application Settings in Azure App Service:
       * In the Azure Portal, go to your App Service, then navigate to "Configuration" -> "Application settings".
       * Add the following environment variables, which your nrn_search/settings/prod.py expects:
           * DJANGO_SETTINGS_MODULE: Set this to nrn_search.settings.prod
           * SECRET_KEY: Generate a strong, unique secret key for your production environment.
           * DB_NAME: The name of your Azure PostgreSQL database.
           * DB_USER: The admin username for your Azure PostgreSQL database.
           * DB_PASSWORD: The admin password for your Azure PostgreSQL database.
           * DB_HOST: The host name of your Azure PostgreSQL server (e.g., <your-postgres-server-name>.postgres.database.azure.com).
           * DB_PORT: 5432
           * ALLOWED_HOSTS: Your Azure App Service domain (e.g., your-app-name.azurewebsites.net).


   5. Initial Post-Deployment Tasks on Azure:
       * After your first successful deployment via GitHub Actions, you'll need to run database migrations and create a superuser on the Azure
         environment.
       * You can do this by connecting to your App Service's SSH console (available in the Azure Portal under "Development Tools" -> "SSH").
       * Once connected, navigate to your application directory (usually /home/site/wwwroot/) and run:

   1         python manage.py migrate
   2         python manage.py createsuperuser

          (Follow the prompts for createsuperuser).


  This process will set up your continuous deployment pipeline, allowing you to push changes to GitHub and have them automatically deployed to
  Azure.imim
1. Create an Azure Container Registry (ACR)

  Open your terminal (or Azure Cloud Shell) and run the following commands:



    1 # Log in to Azure (if you haven't already)
    2 az login
    3
    4 # Create your Azure Container Registry
    5 # Resource Group: SurveyRG
    6 # ACR Name: schsbm-nrn-search
    7 # Choose a location (e.g., eastus, westeurope) that is close to your users or other Azure resources
    8 az acr create \
    9     --resource-group SurveyRG \
   10     --name schsbm-nrn-search \
   11     --sku Basic \
   12     --admin-enabled true


  2. Build and Push Your Docker Image to ACR

  Once your ACR is created, you'll build your Docker image locally and push it to your new registry. Make sure you are in your project's root
  directory (where your Dockerfile is located).



    1 # Log in to your Azure Container Registry
    2 az acr login --name schsbm-nrn-search
    3
    4 # Build your Docker image
    5 # The '.' at the end means "build from the Dockerfile in the current directory"
    6 docker build -t nrnsearch-web .
    7
    8 # Tag your Docker image with the ACR login server name
    9 docker tag nrnsearch-web:latest schsbm-nrn-search.azurecr.io/nrnsearch-web:latest
   10
   11 # Push the tagged image to your Azure Container Registry
   12 docker push schsbm-nrn-search.azurecr.io/nrnsearch-web:latest


  3. Go Back to Azure Portal for Deployment Center

  Now that you have an ACR and your image is pushed there:


   * Go back to the Azure Portal.
   * Navigate to your App Service.
   * Go to "Deployment Center".
   * For "Image Source", you should now be able to select "Azure Container Registry".
   * In the "Registry" dropdown, your newly created schsbm-nrn-search should appear. Select it.
   * Choose your image and tag (e.g., nrnsearch-web and latest).
   * Proceed with the rest of the setup for Continuous Deployment. Azure will then configure the GitHub Actions workflow to use this ACR for
     future deployments.


 creating your Azure Container Registry
  (schsbmacr in this case, within SurveyRG).

  Here are the recommended choices for a
  typical Django application deployment:

   1. Registry name: schsbmacr
       * Recommendation: Use this name. It will
         form your registry's full login server
         name (e.g., schsbmacr.azurecr.io).


   2. Location: East US
       * Recommendation: Keep this. It's
         generally best practice to place your
         ACR in the same Azure region as your
         App Service and Azure Database for
         PostgreSQL to minimize latency and
         data transfer costs.


   3. Domain name label scope: Subscription 
      Reuse
       * Recommendation: This is fine for most
         scenarios. It controls how the public
         endpoint for your registry is managed.


   4. Registry domain name:
      schsbmacr-g6bthva7cngmeubv.azurecr.io
       * Recommendation: This is automatically
         generated and is the full URL you'll
         use when pushing and pulling images.
         Just be aware of it.


   5. Use availability zones: (Not applicable
      for Basic tier)
       * Recommendation: You can ignore this
         for the Basic pricing plan.
         Availability Zones are for higher
         availability and are available with
         the Premium tier.


   6. Pricing plan: Basic
       * Recommendation: Start with Basic. It's
         cost-effective and sufficient for
         development, testing, and smaller
         production workloads. You can easily
         scale up to Standard or Premium later
         if you need more storage, higher
         throughput, or advanced features like
         geo-replication.


   7. Role assignment permissions mode 
      (Preview): RBAC Registry Permissions
       * Recommendation: Choose RBAC Registry      
         Permissions. This is the standard and     
         simpler approach for managing access      
         to your registry. The ABAC option
         provides more granular control but is     
         more complex and still in preview.        


  In summary, for your current setup, proceed 
  with the default or suggested values for 
  most options, ensuring your Registry name is
   `schsbmacr` and the Pricing plan is 
  `Basic`.




