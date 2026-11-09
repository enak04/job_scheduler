"""Maps each job_type to the Python function that runs it."""

from typing import Any, Callable

Payload = dict[str, Any]
Handler = Callable[[Payload], None]

_handlers: dict[str, Handler] = {}


class UnknownJobType(Exception):
    """No handler is registered for this job_type."""


def handler(job_type: str) -> Callable[[Handler], Handler]:
    """Decorator that registers a function as the handler for job_type."""

    def register(func: Handler) -> Handler:
        if job_type in _handlers:
            raise ValueError(f"handler already registered for {job_type!r}")
        _handlers[job_type] = func
        return func

    return register


def get_handler(job_type: str) -> Handler:
    """Return the handler for job_type, or raise UnknownJobType."""
    try:
        return _handlers[job_type]
    except KeyError:
        raise UnknownJobType(job_type) from None


@handler("echo")
def echo(payload: Payload) -> None:
    print(f"echo: {payload}")


@handler("send_email")
def send_email(payload: Payload) -> None:
    # A stand-in until there is a real email service to call.
    print(f"pretending to email {payload['to']}")
