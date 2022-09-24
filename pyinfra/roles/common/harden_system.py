from pyinfra.api import deploy
from pyinfra.operations import files, server

from util import get_file_path


@deploy("Harden system")
def apply():
	# General system hardening via sysctl
	sysctl_hardening = files.put(
		name = "Install system hardening sysctl configuration",
		src = get_file_path("sysctl-hardening.conf"),
		dest = "/etc/sysctl.d/95-system-hardening.conf",
		user = "root",
		group = "root",
		mode = "0644",
	)
	if sysctl_hardening.changed:
		server.systemd.service(
			name = "Apply sysctl configuration",
			service = "systemd-sysctl.service",
			restarted = True,
		)

	# Hide processes and related info from other users (by setting hidepid=invisible on /proc)
	server.group(
		name = "Create proc group for bypassing hidepid",
		group = "proc",
		system = True,
	)
	fstab_hidepid_result = files.line(
		name = "Hide process information from other users (hidepid=invisible)",
		path = "/etc/fstab",
		line = "^proc /proc.*$",
		replace = "proc /proc proc nosuid,nodev,noexec,hidepid=invisible,gid=proc 0 0",
	)
	files.put(
		name = "Install override for systemd-logind to bypass hidepid",
		src = get_file_path("hidepid-systemd-logind-override.conf"),
		dest = "/etc/systemd/system/systemd-logind.service.d/hidepid-bypass.conf",
		create_remote_dir = True,
		user = "root",
		group = "root",
		mode = "0644",
	)
	# Apply change immediately by remounting /proc
	if fstab_hidepid_result.changed:
		server.shell(
			name = "Remount procfs to apply hidepid option",
			commands = "mount -o remount /proc",
		)
