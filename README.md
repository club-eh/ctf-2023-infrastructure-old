# Infrastructure - club.eh CTF 2023

This is the infrastructure monorepo for the 2023 club.eh CTF.


## Environments

Broadly speaking, there are three distinct deployment environments:

| Name | Tool | Description |
| --- | --- | --- |
| Production | Terraform | The environment that will be used during the actual CTF. |
| Staging | Terraform | The environment that will be used for testing in the months leading up to the CTF. |
| Local | Vagrant | Anyone can spin up their own local environment for testing or debugging. |

In all three environments, Ansible is used to manage the machines on the OS-level and below.
