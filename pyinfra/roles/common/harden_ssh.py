from pyinfra.operations import files, server

from lib.users import ensure_user_in_groups


# Make sure `ssh-users` group exists
server.group(
	name = "Create SSH users group",
	group = "ssh-users",
)
# Add management user to ssh-users group
ensure_user_in_groups(
	name = "Add management user to SSH users group",
	user = "management",
	groups = ["ssh-users"],
)

# Harden SSH daemon
sshd_hardening = files.put(
	name = "Install SSH configuration",
	src = "files/common/sshd_config",
	dest = "/etc/sshd_config.d/20-custom.conf",
	user = "root",
	group = "root",
	mode = "0600",
)
if sshd_hardening.changed:
	server.systemd.service(
		name = "Restart SSH daemon to apply configuration",
		service = "sshd.service",
		restarted = True,
	)
