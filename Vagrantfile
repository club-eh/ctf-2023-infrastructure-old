# Vagrantfile for creating a local test environment using VirtualBox

ENV["LC_ALL"] = "en_US.UTF-8"

Vagrant.configure("2") do |config|
  # Use vanilla Fedora 36 (to match production)
  config.vm.box = "bento/fedora-36"

  # Create private network for both machines
  config.vm.network "private_network", type: "dhcp"

  # Disable default shared folder
  config.vm.synced_folder ".", "/vagrant", disabled: true

  # Share DNF cache (to avoid re-downloading files)
  config.vm.synced_folder ".package-cache", "/var/cache/dnf",
    owner: "root", group: "root",
    create: true  # create host directory if needed

  # VirtualBox configuration
  config.vm.provider "virtualbox" do |vb|
    # 4 cores per machine
    vb.cpus = 4

    # 1GB of RAM per machine
    vb.memory = 1024

    # Use linked clones for disk images
    vb.linked_clone = true
  end

  # Define machines
  config.vm.define "flagship-machine"
  config.vm.define "challenge-machine"

  # Use Ansible to provision machines (with an auto-generated inventory file)
  # Note that Vagrant runs Ansible against each machine independently
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "site.yaml"
    ansible.groups = {
      "flagship" => ["flagship-machine"],
      "challenges" => ["challenge-machine"]
    }
  end
end
