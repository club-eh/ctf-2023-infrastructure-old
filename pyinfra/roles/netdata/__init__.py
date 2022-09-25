# Install + configure Netdata

from pyinfra import host, inventory
from pyinfra.api import deploy
from pyinfra.facts.rpm import RpmPackages
from pyinfra.operations import files, server

from util import Flag, KeySource, get_file_path, notify


@deploy("Netdata")
def apply():
	reload_systemd = Flag()
	restart_netdata = Flag()

	if "netdata-repo-edge" not in host.get_fact(RpmPackages).keys():
		server.dnf.rpm(
			name = "Install Netdata repo",
			src = "https://packagecloud.io/netdata/netdata/packages/fedora/36/netdata-repo-edge-1-2.noarch.rpm/download.rpm",
			_serial = host.data.dnf_serial,
		)

	notify(server.dnf.packages(
		name = "Install Netdata",
		packages = ["netdata"],
		_serial = host.data.dnf_serial,
	), reload_systemd)

	notify(files.put(
		name = "Disable Netdata Cloud integration",
		src = get_file_path("cloud.conf"),
		dest = "/var/lib/netdata/cloud.d/cloud.conf",
		user = "root",
		group = "netdata",
		mode = "640",
	), restart_netdata)
	notify(files.file(
		name = "Disable Netdata analytics",
		path = "/etc/netdata/.opt-out-from-anonymous-statistics",
		present = True,
		user = "root",
		group = "netdata",
		mode = "0640",
	), restart_netdata)

	notify(files.template(
		name = "Install main Netdata config",
		src = get_file_path("netdata.conf.j2"),
		dest = "/etc/netdata/netdata.conf",
		user = "root",
		group = "netdata",
		mode = "640",

		netdata_parent = host.data.netdata_parent,
		intnet_ip = host.data.intnet_ip,
	), restart_netdata)

	notify(files.template(
		name = "Install streaming Netdata config",
		src = get_file_path("stream.conf.j2"),
		dest = "/etc/netdata/stream.conf",
		user = "root",
		group = "netdata",
		mode = "640",

		netdata_parent = host.data.netdata_parent,
		parent_ip = inventory.get_host("ctf-flagship").data.intnet_ip,
		netdata_streaming_key = KeySource.derive_key_uuid(host, "netdata-streaming-api-key"),
		children = {
			child.data.hostname : KeySource.derive_key_uuid(child, "netdata-streaming-api-key")
			for child in inventory
			if getattr(child.data, "netdata_parent", None) is False
		},
	), restart_netdata)

	server.systemd.service(
		name = "Activate Netdata service",
		service = "netdata.service",
		running = True,
		enabled = True,
		restarted = restart_netdata,
		daemon_reload = reload_systemd,
	)
