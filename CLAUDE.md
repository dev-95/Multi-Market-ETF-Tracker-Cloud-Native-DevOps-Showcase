# CLAUDE.md — Operator Notes

## What this project is

Portfolio DevOps showcase. Flask web service fetching live ETF prices (Reliance, NiftyBees, VFV.TO, CPX.TO) via yfinance, deployed to Azure as a Docker container. The point is the lifecycle: CI/CD + IaC + observability, not the app itself.

## Architecture

```
Flask + gunicorn (app/tracker.py)
  → Docker image (devesh0905/etf-tracker, built in CI)
  → Azure Linux Web App (etf-tracker-app-dev-95, canadacentral, F1 free tier)
  → provisioned by Terraform (remote state in Azure Blob Storage)
```

**Terraform remote backend:**
- Resource group: `tfstate-rg`
- Storage account: `devesh0905tfstate`
- Container: `tfstate`
- Key: `etf-tracker.tfstate`

Run `terraform init -migrate-state` after any backend config change. Azure CLI must be authenticated first (`az login`).

## CI/CD pipeline (`.github/workflows/terraform.yml`)

Three jobs, strictly in order:

1. **test** — installs `requirements.txt` + `requirements-dev.txt`, runs `pytest app/test_tracker.py -v`
2. **docker** (`needs: test`) — builds `./app`, pushes `devesh0905/etf-tracker:latest` and `devesh0905/etf-tracker:<sha>` to Docker Hub
3. **terraform** (`needs: docker`) — `fmt -check` → `validate` → `plan` → `apply -auto-approve`

Failing tests block everything downstream. `apply` auto-approves on every push to `main` — there is no manual gate yet.

## Local observability stack

`docker compose up --build` starts Flask + Prometheus + Grafana. This is for local dev/demo only — **do not attempt to deploy Prometheus or Grafana to Azure**.

Grafana is fully provisioned from `grafana/provisioning/` on startup — never configure it manually via the UI. Dashboards and alert rules are dashboard-as-code (JSON + YAML in `grafana/`).

Telegram alerting fires when `etf_ticker_fetch_success == 0` for any ticker sustained 1+ minute. Bot token lives in `.env` (gitignored). Chat ID is hardcoded in `grafana/provisioning/alerting/contact-points.yml` as a quoted string — the env var approach caused Grafana 12 to unmarshal it as a number.

## Key facts / gotchas

- **Never re-add `terraform.tfstate` to git.** It was committed by mistake early on, removed with `git rm --cached`. `.gitignore` covers `*.tfstate` and `*.tfstate.backup`.
- **`serverFarms` has a capital F** in the Azure resource ID — matters if running `terraform import` on the App Service Plan.
- **`apply` is ungated** — any push to `main` triggers a live infra change. Flag this before touching `main.tf` or `variables.tf`.
- **Docker Hub repo:** `devesh0905/etf-tracker`
- **Live URL:** `https://etf-tracker-app-dev-95.azurewebsites.net`

## Conventions

- Terraform: all hardcoded values extracted to `variables.tf` with defaults. Never put literals directly in `main.tf`.
- Python deps: production in `requirements.txt` (pinned), test-only in `requirements-dev.txt` (pinned). Neither file uses unpinned ranges.
- Tests: all yfinance calls mocked — no network dependency. 8 tests in `app/test_tracker.py`.
- Grafana: every panel, alert rule, contact point, and datasource is in `grafana/provisioning/` as YAML/JSON. If it's not in a file, it won't survive a container restart.

## Pending / future work

- Manual approval gate before `terraform apply` (currently auto-approves)
- Frontend UI (not yet built — the app is JSON-only today)
- Terraform remote backend provisioning is defined but `terraform init -migrate-state` must be run manually before CI can use it (requires the Azure Storage resources to exist first)
