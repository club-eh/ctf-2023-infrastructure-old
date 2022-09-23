# Common system-wide changes for all machines

from pyinfra import config, local
from pyinfra.operations import server, files


# Use sudo by default
config.SUDO = True


local.include("roles/common/harden_system.py")
local.include("roles/common/harden_ssh.py")

# TODO: harden + secure SSH
# TODO: enable and configure FirewallD
