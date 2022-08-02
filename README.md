# Infrastructure - club.eh CTF 2023

This is the infrastructure repo for the 2023 club.eh CTF.


## Environments

Broadly speaking, we have three distinct deployment environments:

| Name | Tool | Description |
| --- | --- | --- |
| Production | Terraform | The environment that will be used during the actual CTF. |
| Staging | Terraform | The environment that will be used for testing in the months leading up to the CTF. |
| Local | Vagrant | Anyone can spin up their own local environment for testing or debugging. |

In all three environments, Ansible is used to manage the machines at the OS-level.

Staging should be as close to production as possible, with most differences handled by separate Terraform scripts.


## Setting up a local environment

### Prerequisites

- A Unix-y environment with Bash and OpenSSH
- 2 GB of free RAM (each machine uses 1 GB by default)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/installation_distros.html) (only ansible-core is required)
- [Vagrant](https://www.vagrantup.com/docs/installation)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads) (used as Vagrant's backend - other backends are untested)

### Initial Setup

Install the required Ansible collections:

```
ansible-galaxy install -r requirements.yaml
```

Generate a set of secrets for local use:

```
./generate-secrets.sh local
```

### Deployment and Provisioning

Bring up the virtual machines with Vagrant:

```
vagrant up
```

Finish provisioning the machines with Ansible:

```
ansible-playbook -i inventories/local-vagrant.ini site.yaml
```

### Machine Management

At this point, you should have 2 VMs running in VirtualBox, fully provisioned[^1].

[^1]: the Ansible playbooks are still a work-in-progress - the machines don't actually do much yet.

The flagship machine should be accessible at `192.168.61.10` and via `vagrant ssh ctf-flagship`.  
The challenge machine should be accessible at `192.168.61.11` and via `vagrant ssh ctf-challenges-1`.

The machines can be suspended, shut down, etc. via Vagrant's CLI (see `vagrant --help`).  
Note that `vagrant provision` will only apply the initial provision steps, instead of the full site-wide playbook (use `ansible-playbook` for that instead).

All data is ephemeral (for now, until persistence is implemented); running `vagrant destroy` will wipe the machines and all state they contain.

To redeploy from scratch: tear down the environment with `vagrant destroy`, and then follow the [deployment and provisioning](#deployment-and-provisioning) steps.
