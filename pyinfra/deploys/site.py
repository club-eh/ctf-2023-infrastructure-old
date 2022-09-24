# Site-wide deployment (without stateless changes; ex. upgrading to the latest packages)

from roles import base, common, intnet


# Initial system preparation
base.apply()

# Common system / package / security changes for all machines
common.apply()

# Setup internal Wireguard network
intnet.apply()
