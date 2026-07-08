# 📈 Multi-Market ETF Tracker: A DevOps Showcase

> A fully automated, cloud-native application that tracks real-time price data for Indian and Canadian ETFs — built to demonstrate a complete DevOps lifecycle from local development to cloud deployment.

---

## 📖 Project Overview

This project monitors real-time market data for selected ETFs including **Reliance**, **Nifty 50**, **VFV.TO**, and **CPX.TO** (Canadian market).

The application is a **Flask web service** (served via gunicorn) with two HTTP endpoints: a `/` route that returns live ETF market data as JSON, and a `/health` route for App Service health checks. It is deployed as an Azure Linux Web App, pulling a Docker image from Docker Hub.

The focus of this repository is not just the Python application itself, but the **end-to-end DevOps lifecycle**: from local development and containerization, to automated cloud infrastructure provisioning using Infrastructure as Code (IaC).

---

## 🌐 Live Deployment

| Endpoint | URL |
|----------|-----|
| Market Data (JSON) | https://etf-tracker-app-dev-95.azurewebsites.net/ |
| Health Check | https://etf-tracker-app-dev-95.azurewebsites.net/health |

---

## 🏗️ Architecture & Workflow

```
Develop → Package → Ship → Provision → Automate
```

| Stage | Description |
|-------|-------------|
| **Develop** | Flask web service monitors financial markets using real-time APIs and returns JSON responses |
| **Package** | Application is containerized with Docker for environment parity |
| **Ship** | Versioned images pushed to Docker Hub (`devesh0905/etf-tracker`), tagged with both `latest` and git SHA |
| **Provision** | Terraform creates Azure Resource Group, VNet, and Linux Web App in `canadacentral` |
| **Automate** | GitHub Actions runs on every push to `main`: builds and pushes the Docker image, then runs `terraform fmt/validate/plan/apply` automatically |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11 |
| Web Framework | Flask |
| WSGI Server | gunicorn |
| Containerization | Docker |
| Container Registry | Docker Hub |
| Infrastructure (IaC) | Terraform |
| Cloud Provider | Microsoft Azure (App Services) |
| CI/CD | GitHub Actions |

---

## 🚀 Deployment Guide

### Prerequisites
- Azure CLI installed and authenticated (`az login`)
- Docker installed and running
- Terraform installed (`>= 1.0`)
- Docker Hub account

### Step 1 — Build & Push the Docker Image

```bash
docker build -t etf-tracker ./app
docker tag etf-tracker devesh0905/etf-tracker:latest
docker push devesh0905/etf-tracker:latest
```

### Step 2 — Provision Azure Infrastructure

```bash
terraform init
terraform apply -auto-approve
```

### Step 3 — Test the running service

```bash
# Local (after docker run -p 8000:8000 devesh0905/etf-tracker)
curl http://localhost:8000/
curl http://localhost:8000/health

# Live Azure deployment
curl https://etf-tracker-app-dev-95.azurewebsites.net/
curl https://etf-tracker-app-dev-95.azurewebsites.net/health
```

The `/` endpoint returns a JSON array like:
```json
[
  {"ticker": "RELIANCE.NS", "price": 1275.90, "change_pct": -2.48},
  {"ticker": "NIFTYBEES.NS", "price": 271.69, "change_pct": -1.93},
  {"ticker": "VFV.TO",       "price": 187.94, "change_pct": -0.42},
  {"ticker": "CPX.TO",       "price": 74.40,  "change_pct":  2.04}
]
```

If a ticker fetch fails (network error, missing data), that entry includes an `"error"` field instead of price/change, and the rest of the tickers are still returned.

---

## 📊 Monitoring

Application logs can be monitored in real-time via the **Azure Portal Log Stream**.

The gunicorn server logs each request; the application logs each ticker fetch attempt, success, and failure using Python's standard `logging` module. Fetch errors are visible in the log stream without crashing the service.

---

## 🧪 Troubleshooting & Lessons Learned

Real-world cloud deployments rarely go smoothly. Here are the major architectural hurdles encountered and resolved during this project:

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

### 3. One-Shot Script vs. Long-Running Web Server

**Challenge:** The original `tracker.py` was a console script that printed ETF data to stdout and exited. Deployed as an Azure Linux Web App (which expects a persistent HTTP server), the container would start, exit immediately, and crash-loop indefinitely — the app never actually served traffic.

**Solution:** Converted the application to a Flask web service with gunicorn as the WSGI server. The existing yfinance market-data logic was kept intact and wrapped in a `/` route returning JSON. A `/health` route was added for App Service health checks. The Dockerfile CMD was updated from `python tracker.py` to `gunicorn --bind 0.0.0.0:8000 tracker:app`.

---

### 4. Terraform State File Hygiene

**Challenge:** `terraform.tfstate` (and its backup) were committed to git early in the project. State files can contain sensitive resource identifiers and should never be in version control.

**Solution:** The files were removed from git tracking using `git rm --cached` and `.gitignore` was verified to exclude `*.tfstate` and `*.tfstate.backup`. The files remain on disk for local use but are no longer tracked. The correct long-term fix is a remote backend (e.g. Azure Blob Storage) so state is shared, locked, and never touches the local filesystem.

---

## 📁 Project Structure

```
.
├── main.tf                   # Core Terraform resources (App Service, VNet, RG)
├── providers.tf              # AzureRM provider configuration
├── .gitignore                # Excludes .tfstate, __pycache__, and .terraform/
├── .github/
│   └── workflows/
│       └── terraform.yml     # CI/CD pipeline (Docker build + Terraform)
└── app/
    ├── Dockerfile            # Container definition (python:3.11-slim + gunicorn)
    ├── requirements.txt      # Pinned Python dependencies
    └── tracker.py            # Flask web service (yfinance market data)
```

---

## 👤 Author

**Devesh Chowdary Chalasani**  
Cloud & DevOps Engineer  
[LinkedIn](https://linkedin.com/in/) • [Docker Hub](https://hub.docker.com/u/devesh0905)
