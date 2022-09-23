from typing import Callable, Iterable

from pyinfra.api.operation import OperationMeta


class Reactor:
	__slots__ = ("_triggered", )

	def __init__(self):
		self._triggered = False

	def notify(self, operation: OperationMeta):
		pass

	@property
	def triggered(self) -> bool:
		return self._triggered


def notify(operation: OperationMeta, reactors: "Reactor" | Iterable["Reactor"], condition: Callable[[OperationMeta], bool] | None = None):
	"""Notify a Reactor or multiple Reactors when the operation results in a change
	(or when a given condition function returns True).

	Args:
		operation: The return value of the operation to respond to.
		reactors: One or more Reactor instances to notify if the condition is True.
		condition (optional): A function to determine whether the reactors should be notified, given the operation result.
		Defaults to checking whether the operation changed anything or not.
	"""

	if condition is None:
		should_notify = operation.changed
	else:
		should_notify = condition(operation)

	if should_notify:
		if isinstance(reactors, Reactor):
			reactors._triggered = True
		else:
			for reactor in reactors:
				reactor._triggered = True
