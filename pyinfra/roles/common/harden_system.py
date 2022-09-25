from pyinfra import host
from pyinfra.api import deploy, operation
from pyinfra.facts.files import FindInFile
from pyinfra.operations import files, server

from util import Flag, get_file_path, notify


CONFIG_FILE_PERMS = {
	"user": "root",
	"group": "root",
	"mode": "0644",
}


@operation
def lock_root_account():
	# look for '^root:!!' in /etc/shadow; if it matches, the root account is locked
	root_shadow_locked = host.get_fact(FindInFile, path="/etc/shadow", pattern=r"^root\:\!\!")

	if root_shadow_locked is None or len(root_shadow_locked) == 0:
		yield from server.shell("passwd -l root")
	else:
		host.noop("root account is already locked")


@deploy("Harden system")
def apply():
	reload_systemd = Flag()

	# Remove packages
	notify(server.dnf.packages(
		name = "Remove unused packages",
		present = False,
		packages = [
			# NFS support
			"nfs-utils", "libnfsidmap",
			# SSSD support (central identity management software)
			"sssd-common",
			# software RAID support
			"mdadm",
			# PC/SC smart card support
			"pcsc-lite",
		],
		_serial = host.data.dnf_serial,
	), reload_systemd)

	# General system hardening via sysctl
	sysctl_hardening = files.put(
		name = "Install system hardening sysctl configuration",
		src = get_file_path("sysctl-hardening.conf"),
		dest = "/etc/sysctl.d/95-system-hardening.conf",
		**CONFIG_FILE_PERMS,
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
	logind_override = files.put(
		name = "Install override for systemd-logind to bypass hidepid",
		src = get_file_path("hidepid-systemd-logind-override.conf"),
		dest = "/etc/systemd/system/systemd-logind.service.d/hidepid-bypass.conf",
		create_remote_dir = True,
		**CONFIG_FILE_PERMS,
	)
	if logind_override.changed:
		server.systemd.service(
			name = "Restart systemd-logind",
			service = "systemd-logind.service",
			restarted = True,
			daemon_reload = True,
		)

	# Apply hidepid setting immediately by remounting /proc
	if fstab_hidepid_result.changed:
		server.shell(
			name = "Remount procfs to apply hidepid option",
			commands = "mount -o remount /proc",
		)

	# Restrict su to wheel group
	files.put(
		name = "Restrict `su` access to members of wheel group",
		src = get_file_path("pam-su.conf"),
		dest = "/etc/pam.d/su",
		**CONFIG_FILE_PERMS,
	)

	# Lock root account to prevent direct root login
	lock_root_account(name="Lock root account")


	# Reload systemd daemon if needed
	if reload_systemd:
		server.systemd.daemon_reload()
