# Infrastructure - club.eh CTF 2023

This is our (old) infrastructure repo for the 2023 club.eh CTF.

See our [v2 repo](https://github.com/club-eh/ctf-2023-infrastructure) for the infrastructure we actually used during Hacker's Odyssey CTF.


## Preface

This repository has two branches: `pyinfra` (this one) and `ansible`.

We started writing our IaC using [Ansible](https://ansible.com/), but eventually looked for an alternative that "stayed out of the way" a bit more.  
[Pyinfra](https://pyinfra.com/) seemed to fit the bill (although it has its own issues), so I rewrote everything in Pyinfra.  
I also wrote a few hacky patches that I didn't bother to upstream, which can be found [here](https://git.sb418.net/sudoBash418/pyinfra).

After some outside developments, including a switch to Microsoft Azure, we decided to abandon this repo entirely in favour of a Kubernetes-based infrastructure.


## Environments

Broadly speaking, we have three distinct deployment environments:

| Name | Host | Description |
| --- | --- | --- |
| Production | Azure | The environment that will be used during the actual CTF. |
| Staging | Proxmox | The environment that will be used for challenge development / testing in the months leading up to the CTF. |
| Local | Vagrant | Anyone can spin up their own local environment for testing or debugging. |

In all three environments, pyinfra is used to manage the machines at the OS-level (ie. taking machines from stock VM to CTFd or Docker).

For VM provisioning (management of the virtual hardware itself):
- Production and staging will use Terraform (likely with some custom scripts as well)
- Local environments use Vagrant

In general, staging should be as close to production as reasonably possible.


## Setting up a local environment

### Prerequisites

- A Unix-y environment with Bash and OpenSSH
- 2 GB of free RAM (each machine uses 1 GB by default)
- [Poetry](https://python-poetry.org/docs/) (for pyinfra)
- [Vagrant](https://www.vagrantup.com/docs/installation)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads) (used as Vagrant's backend - other backends are untested)

### Initial Setup

Generate a set of secrets for local use:

```bash
./generate-secrets.sh local
```

Create a virtualenv and install dependencies:

```bash
cd pyinfra/
poetry install
```

### Deployment and Provisioning

Bring up the virtual machines with Vagrant:

```bash
cd vagrant/
vagrant up
```

Provision the machines with pyinfra:

```bash
cd pyinfra/
# Enter virtualenv
poetry shell
# Initial deployment steps (only needs to be run once, unless you're working on pre-init deployment code)
pyinfra inventories/local-vagrant-bootstrap.py deploys/initial.py
# Full "site-wide" deployment. run this again to apply changes to pyinfra deployment code
pyinfra inventories/local-vagrant.py deploys/site.py
```

### Machine Management

At this point, you should have 2 VMs running in VirtualBox, fully provisioned.

The flagship machine should be accessible at `192.168.61.10` and via `vagrant ssh ctf-flagship`.  
The challenge machine should be accessible at `192.168.61.11` and via `vagrant ssh ctf-challenges-1`.

The machines can be suspended, shut down, etc. via Vagrant's CLI (see `vagrant --help`).

All data is ephemeral in the local environment; running `vagrant destroy` will wipe the machines and all state they contain.

To redeploy from scratch: tear down the environment with `vagrant destroy`, and then follow the [deployment and provisioning](#deployment-and-provisioning) steps.
