variable "resource_group_name" {
  default = "portfolio-resources"
}

variable "location" {
  default = "canadacentral"
}

variable "app_name" {
  default = "etf-tracker-app-dev-95"
}

variable "docker_image_name" {
  default = "devesh0905/etf-tracker:latest"
}

variable "sku_name" {
  default = "F1"
}
