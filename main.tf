resource "azurerm_resource_group" "portfolio_rg" {
  name     = "portfolio-resources"
  location = "canadacentral"
}

resource "azurerm_virtual_network" "main_vnet" {
  name                = "portfolio-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.portfolio_rg.location
  resource_group_name = azurerm_resource_group.portfolio_rg.name
}

# Create the App Service Plan (The server hosting the app)
resource "azurerm_service_plan" "app_plan" {
  name                = "portfolio-app-plan"
  resource_group_name = azurerm_resource_group.portfolio_rg.name
  location            = azurerm_resource_group.portfolio_rg.location
  os_type             = "Linux"
  sku_name            = "F1" # Free Tier
}

# Create the Web App and point it to your Docker image
resource "azurerm_linux_web_app" "etf_app" {
  name                = "etf-tracker-app-dev-95"
  resource_group_name = azurerm_resource_group.portfolio_rg.name
  location            = azurerm_resource_group.portfolio_rg.location
  service_plan_id     = azurerm_service_plan.app_plan.id

  site_config {
    always_on = false
    application_stack {
      # This is the cleanest way to reference a public Docker Hub image
      docker_image_name   = "devesh0905/etf-tracker:latest"
      docker_registry_url = "https://index.docker.io"
    }
  }
}