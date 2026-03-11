# 📈 Multi-Market ETF Tracker: A DevOps Showcase

> A fully automated, cloud-native application that tracks real-time price data for Indian and Canadian ETFs — built to demonstrate a complete DevOps lifecycle from local development to cloud deployment.

---

## 📖 Project Overview

This project monitors real-time market data for selected ETFs including **Reliance**, **Nifty 50**, and **VFV.TO** (Canadian market).

The focus of this repository is not just the Python application itself, but the **end-to-end DevOps lifecycle**: from local development and containerization, to automated cloud infrastructure provisioning using Infrastructure as Code (IaC).

---

## 🏗️ Architecture & Workflow

```
Develop → Package → Ship → Provision → Automate
```

| Stage | Description |
|-------|-------------|
| **Develop** | Python script monitors financial markets using real-time APIs |
| **Package** | Application is containerized with Docker for environment parity |
| **Ship** | Versioned images pushed to Docker Hub (`devesh0905/etf-tracker`) |
| **Provision** | Terraform creates Azure Resource Group, VNet, and Linux Web App in `canadacentral` |
| **Automate** | *(Optional)* GitHub Actions integration for automated infrastructure updates |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.x |
| Containerization | Docker |
| Container Registry | Docker Hub |
| Infrastructure (IaC) | Terraform |
| Cloud Provider | Microsoft Azure (App Services) |
| CI/CD | GitHub Actions *(optional)* |

---

## 🚀 Deployment Guide

### Prerequisites
- Azure CLI installed and authenticated (`az login`)
- Docker installed and running
- Terraform installed (`>= 1.0`)
- Docker Hub account

### Step 1 — Build & Push the Docker Image

```bash
docker build -t etf-tracker .
docker tag etf-tracker devesh0905/etf-tracker:latest
docker push devesh0905/etf-tracker:latest
```

### Step 2 — Provision Azure Infrastructure

```bash
terraform init
terraform apply -auto-approve
```

---

## 📊 Monitoring

Application logs can be monitored in real-time via the **Azure Portal Log Stream**.

Upon startup, the container pulls the latest image and outputs live ETF market data directly to the console.

---

## 🧪 Troubleshooting & Lessons Learned

Real-world cloud deployments rarely go smoothly. Here are two major architectural hurdles encountered and resolved during this project:

### 1. Navigating Regional Cloud Quotas

**Challenge:** Encountered `401 Unauthorized` errors when deploying to `eastus` due to subscription-level limitations on Free Tier (F1) resources.

**Solution:** Refactored Terraform configuration to migrate the entire stack to `canadacentral`, ensuring 100% resource availability while remaining within free tier budget constraints.

---

### 2. Resolving Docker Registry Path Conflict

**Challenge:** Azure App Service logs reported `BadRequest` and `invalid reference format` errors during the Docker image pull phase.

**Solution:** Identified a syntax conflict where Azure was prepending extra slashes to the image name. Resolved by explicitly defining the Docker V1 Registry URL (`https://index.docker.io/v1`) within the Terraform `application_stack` block.

```hcl
application_stack {
  docker_registry_url = "https://index.docker.io/v1"
  docker_image_name   = "devesh0905/etf-tracker:latest"
}
```

---

## 📁 Project Structure

```
.
├── main.tf               # Core Terraform resources (App Service, VNet, RG)
├── providers.tf          # AzureRM provider configuration
├── Dockerfile            # Container definition
├── app.py                # Python ETF tracking script
└── .gitignore            # Excludes .tfstate, secrets, and keys
```

---

## 👤 Author

**Devesh Chowdary Chalasani**  
Cloud & DevOps Engineer  
[LinkedIn](https://linkedin.com/in/) • [Docker Hub](https://hub.docker.com/u/devesh0905)
