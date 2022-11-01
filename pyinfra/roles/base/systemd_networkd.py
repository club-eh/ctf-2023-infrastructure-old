# Replace NetworkManager with systemd-networkd

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.systemd import SystemdStatus
from pyinfra.operations import dnf, files, systemd

from util import Flag, get_file_path, notify
from util.paths import PathNotFound


@deploy("Install + configure systemd-networkd")
def apply():
	reload_systemd = Flag()
	restart_networkd = Flag()


	notify(dnf.packages(
		name = "Install systemd-networkd",
		packages = ["systemd-networkd"],
		_serial = host.data.dnf_serial,
	), reload_systemd)

	# only try to disable NetworkManager service if it existed originally
	# otherwise, pyinfra runs this operation every time
	if "NetworkManager.service" in host.get_fact(SystemdStatus).keys():
		systemd.service(
			name = "Disable and deactivate NetworkManager",
			service = "NetworkManager.service",
			running = False,
			enabled = False,
		)

	# note: this comes after the disable + stop to avoid issues with missing systemd unit files
	notify(dnf.packages(
		name = "Remove NetworkManager",
		packages = ["NetworkManager"],
		present = False,
		_serial = host.data.dnf_serial,
	), reload_systemd)


	notify(files.put(
		name = "Install default network configuration",
		src = get_file_path("80-wired.network"),
		dest = "/etc/systemd/network/80-wired.network",
		user = "root",
		group = "root",
		mode = "0644",
	), restart_networkd)

	for group_name in host.groups:
		try:
			template_file = get_file_path(f"10-static-{group_name}.network.j2")
		except PathNotFound:
			pass
		else:
			notify(files.template(
				name = f"Install static IP network configuration for '{group_name}'",
				src = template_file,
				dest = "/etc/systemd/network/10-static.network",
				user = "root",
				group = "root",
				mode = "0644",
			), restart_networkd)


	systemd.service(
		name = "Activate systemd-networkd",
		service = "systemd-networkd.service",
		running = True,
		enabled = True,
		restarted = restart_networkd,
		daemon_reload = reload_systemd,
	)
