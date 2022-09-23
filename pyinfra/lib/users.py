from typing import Iterable

from pyinfra import host
from pyinfra.api import operation, StringCommand
from pyinfra.facts.server import Groups, Users


@operation
def ensure_user_in_groups(user: str, groups: Iterable[str]):
	"""Adds a user to a list of groups.

	Args:
		user: Username of the user to modify.
		groups: The groups that the user should be a member of.
	"""

	target_groups = set(groups)

	_users = host.get_fact(Users)
	_groups = host.get_fact(Groups)

	user_data = _users.get(user)
	if user_data is None:
		raise ValueError(f"User '{user}' does not exist")

	# ensure all target groups actually exist
	if len(target_groups.difference(_groups)):
		raise ValueError(f"Groups '{target_groups.difference(_groups)}' do not exist")

	missing_groups = target_groups.difference(user_data["groups"])

	if len(missing_groups):
		yield StringCommand("usermod", "-a", "-G", ','.join(missing_groups), user)
