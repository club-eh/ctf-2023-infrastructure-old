from pyinfra.api import deploy
from pyinfra.operations import files, server

from util import ensure_user_in_groups, get_file_path


@deploy("Configure SSH")
def apply():
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

	# Install + apply SSH config
	sshd_config = files.put(
		name = "Install SSH configuration",
		src = get_file_path("sshd_config"),
		dest = "/etc/sshd_config.d/20-custom.conf",
		user = "root",
		group = "root",
		mode = "0600",
	)
	if sshd_config.changed:
		server.systemd.service(
			name = "Restart SSH daemon to apply configuration",
			service = "sshd.service",
			restarted = True,
		)
