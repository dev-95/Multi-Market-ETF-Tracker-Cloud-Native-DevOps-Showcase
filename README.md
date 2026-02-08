📈 Multi-Market ETF Tracker: A DevOps Showcase
📖 Project Overview
This project is a fully automated, cloud-native application designed to track real-time price data for specific Indian and Canadian ETFs (e.g., Reliance, Nifty 50, and VFV.TO).

The focus of this repository is not just the Python application, but the DevOps lifecycle: from local development and containerization to automated infrastructure provisioning using Infrastructure as Code (IaC).

🏗️ Architecture & Workflow
Develop: Python script monitors financial markets using real-time APIs.

Package: Application is containerized using Docker for environment parity.

Ship: Images are versioned and pushed to Docker Hub (devesh0905/etf-tracker).

Provision: Terraform creates the Azure Resource Group, VNet, and Linux Web App in canadacentral.

Automate: (Optional) Integrated with GitHub Actions for automated infrastructure updates.

🛠️ Tech Stack
Language: Python 3.x

Infrastructure: Terraform

Containerization: Docker

Registry: Docker Hub

Cloud Provider: Microsoft Azure (App Services)

🧪 Lessons Learned & Troubleshooting
Recruiters value problem-solving. During this project, I overcame two major architectural hurdles:

1. Navigating Regional Cloud Quotas
Challenge: Faced 401 Unauthorized errors when deploying to eastus due to subscription-level limitations on Free Tier (F1) resources.

Solution: Refactored Terraform code to migrate the entire stack to canadacentral, ensuring 100% resource availability while remaining within the free tier budget.

2. Resolving Docker Registry Pathing
Challenge: Azure App Service logs reported BadRequest and invalid reference format during the image pull phase.

Solution: Identified a syntax conflict where Azure was prepending extra slashes to the image name. I resolved this by explicitly defining the Docker V1 Registry URL (https://index.docker.io/v1) within the Terraform application_stack block.

🚀 Deployment Guide
1. Build and Push Application
Bash
docker build -t etf-tracker .
docker tag etf-tracker devesh0905/etf-tracker:latest
docker push devesh0905/etf-tracker:latest
2. Provision Infrastructure
Bash
terraform init
terraform apply -auto-approve
📈 Monitoring
The application's real-time logs can be monitored through the Azure Portal Log Stream. Upon startup, the container successfully pulls the latest image and outputs live market data directly to the console.
