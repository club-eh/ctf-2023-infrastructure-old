# Install + configure Nginx

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files, server

from util import Flag, get_file_path, get_secrets_dir, notify


CONFIG_FILE_PERMS = {
	"user": "root",
	"group": "nginx",
	"mode": "0640",
}


@deploy("Nginx")
def apply():
	reload_systemd = Flag()
	reload_nginx = Flag()

	notify(server.dnf.packages(
		name = "Install nginx",
		packages = ["nginx"],
		_serial = host.data.dnf_serial,
	), reload_systemd)

	for filename in ["nginx.conf", "ssl-dhparam.pem"]:
		notify(files.put(
			name = f"Install base config files ({filename})",
			src = get_file_path(filename),
			dest = f"/etc/nginx/{filename}",
			**CONFIG_FILE_PERMS,
		), reload_nginx)

	notify(files.template(
		name = "Install SSL configuration",
		src = get_file_path("ssl.conf.j2"),
		dest = "/etc/nginx/ssl.conf",
		**CONFIG_FILE_PERMS,
	), reload_nginx)

	notify(files.put(
		name = "Install SSL certificate",
		src = get_secrets_dir() / "ssl-certificate.pem",
		dest = "/etc/nginx/ssl/server.crt",
		user = "root",
		group = "nginx",
		mode = "0644",
	), reload_nginx)
	notify(files.put(
		name = "Install SSL private key",
		src = get_secrets_dir() / "ssl-certificate.key",
		dest = "/etc/nginx/ssl/server.key",
		user = "root",
		group = "nginx",
		mode = "0640",
	), reload_nginx)

	site_configs_dir = get_file_path(host.data.primary_group)
	if site_configs_dir.exists():
		for site_config in site_configs_dir.iterdir():
			# determine relative path of site config
			site_config_relpath = site_config.relative_to(site_configs_dir)

			notify(files.template(
				name = f"Install site config ({site_config_relpath})",
				src = site_config,
				dest = f"/etc/nginx/conf.d/{site_config_relpath}",
				**CONFIG_FILE_PERMS,
			), reload_nginx)

	server.systemd.service(
		name = "Activate nginx service",
		service = "nginx.service",
		running = True,
		enabled = True,
		reloaded = reload_nginx,
		daemon_reload = reload_systemd,
	)
