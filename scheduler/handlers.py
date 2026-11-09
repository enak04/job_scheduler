"""Maps each job_type to the Python function that runs it."""

import time
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


# The handlers below are fake: they sleep to simulate slow work.
@handler("send_email")
def send_email(payload: Payload) -> None:
    time.sleep(1)
    print(f"pretending to email {payload['to']}")


@handler("resize_image")
def resize_image(payload: Payload) -> None:
    time.sleep(2)
    print(f"pretending to resize {payload['file']}")


@handler("generate_report")
def generate_report(payload: Payload) -> None:
    time.sleep(3)
    print(f"pretending to generate report {payload['name']}")
