# Site-wide deployment (without stateless changes; ex. upgrading to the latest packages)

from roles import base, common, netdata


# Initial system preparation
base.apply()

# Common setup for all machines
common.apply()

# Netdata setup for all machines
netdata.apply()
