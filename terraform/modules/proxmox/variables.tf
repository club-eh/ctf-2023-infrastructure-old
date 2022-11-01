variable "secrets_dir" {
  type        = string
  description = "Path to the secrets directory."
  nullable    = false
}

variable "api_url" {
  type        = string
  description = "Proxmox API endpoint to connect to."
  nullable    = false
}

variable "pve_node" {
  type        = string
  description = "PVE node to create VMs on."
  nullable    = false
}

variable "pve_pool" {
  type        = string
  description = "PVE pool to create VMs in."
  nullable    = false
}

variable "disk_size_os" {
  type        = string
  description = "Size of OS disks."
  nullable    = false
}
