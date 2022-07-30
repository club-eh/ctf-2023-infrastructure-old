#!/bin/bash

set -e


# generate SSH keypair for management accounts
ssh-keygen -t ed25519 -f secrets/ssh_key -C "Management SSH key"
