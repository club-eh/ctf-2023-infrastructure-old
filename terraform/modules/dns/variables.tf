variable "secrets_dir" {
  type        = string
  description = "Path to the secrets directory."
  nullable    = false
}

variable "domain" {
  type        = string
  description = "Root domain name to create a subdomain on."
  nullable    = false
}

variable "subdomain" {
  type        = string
  description = "Base subdomain to create."
  nullable    = false
}

variable "ip_flagship" {
  type        = string
  description = "IP address pointing to the flagship machine."
  nullable    = false
}

variable "ip_challenges" {
  type        = map(string)
  description = "IP addresses pointing to the challenge machines."
  nullable    = false
}
