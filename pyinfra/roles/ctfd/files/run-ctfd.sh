#!/bin/bash

set -e

# activate venv
source /opt/ctfd/venv/bin/activate

# initialize / migrate database
python3 manage.py db upgrade

# run CTFd via gunicorn
ARGS=(
	# use 6 worker processes
	--workers 6
	# CTFd requires gevent
	--worker-class gevent

	# (disabled) log to proper location (/var/log/ctfd)
	#--access-logfile "${LOGS_DIRECTORY}/access.log"

	# (disabled) faster startup + lower RAM usage
	#--preload  # breaks gevent SSL (throws a MonkeyPatchWarning, eventually resulting in a RecursionError when requests is used)
)
exec python3 -u -m gunicorn 'CTFd:create_app()' "${ARGS[@]}"
