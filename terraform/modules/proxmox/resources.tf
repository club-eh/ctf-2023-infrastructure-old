resource "proxmox_vm_qemu" "test-vm" {
  target_node = var.pve_node
  pool        = var.pve_pool

  vmid = 2300
  name = "tf-test-vm"
  desc = "testing terraform. ignore me (or kill me if I've been alive too long)."

  # TODO: maybe packer?
  clone      = "ctf-template-temp"
  full_clone = false

  cpu     = "host"
  numa    = true
  cores   = 6
  sockets = 1
  memory  = 4096
  bios    = "ovmf"
  qemu_os = "l26"
  scsihw  = "virtio-scsi-single"
  tablet  = false
  agent   = 1

  vga {
    type = "qxl"
    memory = 32
  }

  network {
    model    = "virtio"
    bridge   = "vmbr0"
    firewall = false
  }

  # extra disk (for persist data)
  disk {
    type     = "scsi"
    storage  = "local-lvm"
    size     = var.disk_size_os
    iothread = 1
    ssd      = 1
    discard  = "on"
  }

  cloudinit_cdrom_storage = "local-lvm"

  ciuser    = "management"
  sshkeys   = file("${var.secrets_dir}/staging/management_ssh_key.pub")
  ipconfig0 = "gw=10.7.8.1,ip=10.7.8.220/24"
  ci_wait   = 30
}
