# Vagrantfile for creating a local test environment using VirtualBox

ENV["LC_ALL"] = "en_US.UTF-8"

Vagrant.configure("2") do |config|
  # Use vanilla Fedora 36 (to match production)
  config.vm.box = "bento/fedora-36"

  # Disable default shared folder
  config.vm.synced_folder ".", "/vagrant", disabled: true

  # Share DNF cache (to avoid re-downloading files)
  config.vm.synced_folder ".package-cache", "/var/cache/dnf",
    owner: "root", group: "root",
    create: true  # create host directory if needed

  # VirtualBox configuration
  config.vm.provider :virtualbox do |vb|
    # 4 cores per machine
    vb.cpus = 4

    # 1GB of RAM per machine
    vb.memory = 1024

    # Use linked clones for disk images
    vb.linked_clone = true
  end


  # Define flagship machine
  config.vm.define "flagship-machine" do |machine|
    machine.vm.network :private_network, ip: "192.168.61.10/24"
  end

  # Define challenge machines
  challenge_machine_num = 1
  challenge_machines = []
  (1..challenge_machine_num).each do |mid|
    # generate machine name
    machine_name = "challenge-machine-#{mid}"
    # add to array
    challenge_machines << machine_name
    # define the machine
    config.vm.define machine_name do |machine|
      machine.vm.network :private_network, ip: "192.168.61.#{10 + mid}/24"
    end
  end


  # Use Ansible to semi-provision machines (with an auto-generated inventory file)
  # Note that Vagrant runs Ansible against each machine independently
  config.vm.provision :ansible do |ansible|
    ansible.playbook = "initial.yaml"
    ansible.groups = {
      "flagship" => ["flagship-machine"],
      "challenges" => challenge_machines
    }
    ansible.extra_vars = {
      # prevent conflicts over shared package cache
      dnf_throttle: 1
    }
  end
end
