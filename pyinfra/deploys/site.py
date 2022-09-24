# Site-wide deployment (without stateless changes; ex. upgrading to the latest packages)

from pyinfra import config

from roles import base, common


# Run everything with sudo by default
config.SUDO = True


# Initial system preparation
base.apply()

# Common system / package / security changes for all machines
common.apply()
