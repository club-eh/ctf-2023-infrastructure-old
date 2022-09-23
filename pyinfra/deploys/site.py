# Site-wide deployment (without stateless changes; ex. upgrading to the latest packages)

from pyinfra import local, host, config
from pyinfra.api import deploy


config.TEMP_DIR = "/tmp/pyinfra-deploy"


# Initial system preparation
local.include("roles/base.py")

# Common system / package / security changes for all machines
local.include("roles/common.py")
