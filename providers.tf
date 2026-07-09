terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "devesh0905tfstate"
    container_name       = "tfstate"
    key                  = "etf-tracker.tfstate"
  }
}

provider "azurerm" {
  features {}
}