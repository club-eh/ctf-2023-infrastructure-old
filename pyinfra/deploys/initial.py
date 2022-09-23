# Initial deploy - prepares the system for later deployments

from pyinfra import local


local.include("roles/base.py")
