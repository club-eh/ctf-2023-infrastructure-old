# Basic system configuration, common across all machines

from pyinfra import host, config, local
from pyinfra.operations import server

from lib.timezone import timezone
from lib.secrets import get_secrets_dir


# Run everything with sudo by default
config.SUDO = True


# Create + setup management user
server.user(
	name = "Create management user",
	user = "management",
	comment = "Superuser account used for administration and automation",
	shell = "/bin/bash",
	create_home = True,
	public_keys = [get_secrets_dir(host.data.env_name) / "management_ssh_key.pub"],
)
server.files.put(
	name = "Allow password-less sudo for management user",
	src = "files/base/sudoers_management",
	dest = "/etc/sudoers.d/management",
	user = "root",
	group = "root",
	mode = "0600",
)

# Set hostname and timezone, if specified
if hasattr(host.data, "hostname"):
	server.hostname(
		name = "Set the system hostname",
		hostname = host.data.hostname,
	)
if hasattr(host.data, "timezone"):
	timezone(
		name = "Set the system timezone",
		timezone = host.data.timezone,
	)

# Replace NetworkManager with systemd-networkd
local.include("roles/base/systemd_networkd.py")
