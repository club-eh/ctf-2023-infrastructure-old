terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "~> 2.9.11"
    }
  }
}


# Proxmox provider configuration
provider "proxmox" {
  pm_api_url = var.api_url

  # TODO: remove
  pm_proxy_server = "http://127.0.0.1:8080"

  # Pull API token from secrets file
  pm_api_token_id     = file("${var.secrets_dir}/api_token_proxmox_id")
  pm_api_token_secret = file("${var.secrets_dir}/api_token_proxmox_secret")
}
