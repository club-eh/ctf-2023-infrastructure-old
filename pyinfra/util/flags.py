from typing import Callable, Iterable

from pyinfra.api.operation import OperationMeta


class Flag:
	__slots__ = ("_tripped", )

	def __init__(self):
		self._tripped = False

	def trip(self):
		self._tripped = True

	def __bool__(self) -> bool:
		return self._tripped

	@property
	def tripped(self) -> bool:
		return self._tripped


def notify(operation: OperationMeta, flags: "Flag" | Iterable["Flag"], condition: Callable[[OperationMeta], bool] | None = None):
	"""Trip a Flag (or multiple Flags) when the operation results in a change
	(or when a given condition function returns True).

	Args:
		operation: The return value of the operation to respond to.
		flags: One or more Flag instances to notify if the condition is True.
		condition (optional): A function to determine whether the flags should be notified, given the operation result.
		Defaults to checking whether the operation changed anything or not.
	"""

	if condition is None:
		should_trip = operation.changed
	else:
		should_trip = condition(operation)

	if should_trip:
		if isinstance(flags, Flag):
			flags.trip()
		else:
			for flag in flags:
				flag.trip()
