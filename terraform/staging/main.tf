## Root module for the staging environment

terraform {
  required_version = ">= 1.1.0"
}


locals {
  # Number of challenge server machines to create
  num_challenge_machines = 1
}


# DNS records
module "dns" {
  source = "../modules/dns"

  # Shared variables
  secrets_dir = var.secrets_dir
  domain      = var.domain

  # Subdomain for this environment
  subdomain = "ctf-2023-staging"

  # Static IPs
  ip_flagship   = "10.7.8.100"
  ip_challenges = { for i in range(1, local.num_challenge_machines + 1) : i => "10.7.8.${100 + i}" }
}
