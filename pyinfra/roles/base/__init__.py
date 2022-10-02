# Basic system configuration, common across all machines

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import Selinux
from pyinfra.operations import server

from util import get_file_path, get_secret_path
from util.timezone import timezone

from . import systemd_networkd


@deploy("Base")
def apply():
	# Create + setup management user
	server.user(
		name = "Create management user",
		user = "management",
		comment = "Superuser account used for administration and automation",
		shell = "/bin/bash",
		create_home = True,
		public_keys = [get_secret_path("management_ssh_key.pub")],
	)
	server.files.put(
		name = "Enable password-less sudo for management user",
		src = get_file_path("sudoers_management"),
		dest = "/etc/sudoers.d/management",
		user = "root",
		group = "root",
		mode = "0600",
	)

	# Disable SELinux enforcement
	if host.get_fact(Selinux)["mode"] == "enabled":
		server.shell(
			name = "Disable SELinux enforcement (runtime)",
			commands="setenforce 0",
		)
	server.files.line(
		name = "Disable SELinux enforcement (permanent)",
		path = "/etc/selinux/config",
		line = "SELINUX=enforcing",
		replace = "SELINUX=permissive",
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

	if host.data.env_name == "local":
		server.files.line(
			name = "Enable DNF package cache",
			path = "/etc/dnf/dnf.conf",
			present = True,
			line = "keepcache=1",
		)

	# Replace NetworkManager with systemd-networkd
	systemd_networkd.apply()

	# Ensure /persist exists
	# TODO: ensure volume is mounted in staging/production environments
	server.files.directory(
		name = "Create /persist directory",
		path = "/persist",
		user = "root",
		group = "root",
		mode = "755",
	)
