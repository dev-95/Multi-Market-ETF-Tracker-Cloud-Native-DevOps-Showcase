resource "azurerm_resource_group" "portfolio_rg" {
  name     = "portfolio-resources"
  location = "East US" 
}

resource "azurerm_virtual_network" "main_vnet" {
  name                = "portfolio-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.portfolio_rg.location
  resource_group_name = azurerm_resource_group.portfolio_rg.name
}