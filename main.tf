resource "azurerm_resource_group" "portfolio_rg" {
  name     = var.resource_group_name
  location = var.location
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
  sku_name            = var.sku_name
}

# Create the Web App and point it to your Docker image
resource "azurerm_linux_web_app" "etf_app" {
  name                = var.app_name
  resource_group_name = azurerm_resource_group.portfolio_rg.name
  location            = azurerm_resource_group.portfolio_rg.location
  service_plan_id     = azurerm_service_plan.app_plan.id

  site_config {
    always_on = false
    application_stack {
      # This is the cleanest way to reference a public Docker Hub image
      docker_image_name   = var.docker_image_name
      docker_registry_url = "https://index.docker.io"
    }
  }
}