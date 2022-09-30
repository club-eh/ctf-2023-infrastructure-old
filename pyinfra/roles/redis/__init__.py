# Install + configure Redis

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files, server

from util import Flag, KeySource, get_file_path, notify


@deploy("Redis")
def apply():
	reload_systemd = Flag()
	restart_redis = Flag()

	notify(server.dnf.packages(
		name = "Install Redis",
		packages = ["redis"],
		_serial = host.data.dnf_serial,
	), reload_systemd)

	notify(files.put(
		name = "Lockdown Redis service",
		src = get_file_path("service-lockdown.conf"),
		dest = "/etc/systemd/system/redis.service.d/lockdown.conf",
		user = "root",
		group = "root",
		mode = "644",
	), [reload_systemd, restart_redis])

	notify(files.put(
		name = "Configure Redis",
		src = get_file_path("redis.conf"),
		dest = "/etc/redis/redis.conf",
		user = "root",
		group = "redis",
		mode = "0640",
	), restart_redis)

	notify(files.template(
		name = "Configure Redis users",
		src = get_file_path("users.acl.j2"),
		dest = "/etc/redis/users.acl",
		user = "root",
		group = "redis",
		mode = "0640",

		# derive a unique password for each user
		**{
			f"pwd_{user}" : KeySource.derive_key(host, f"redis-user-pwd-{user}", 32).hex()
			for user in ["admin", "ctfd", "netdata"]
		},
	), restart_redis)

	server.systemd.service(
		name = "Activate Redis service",
		service = "redis.service",
		running = True,
		enabled = True,
		restarted = restart_redis,
		daemon_reload = reload_systemd,
	)
