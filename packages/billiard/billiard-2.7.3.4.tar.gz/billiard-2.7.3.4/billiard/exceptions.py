from __future__ import absolute_import

try:
    from multiprocessing import (
        ProcessError,
        BufferTooShort,
        TimeoutError,
        AuthenticationError,
    )
except ImportError:
    class ProcessError(Exception): pass         # noqa
    class BufferTooShort(Exception): pass       # noqa
    class TimeoutError(Exception): pass         # noqa
    class AuthenticationError(Exception): pass  # noqa


class TimeLimitExceeded(Exception):
    """The time limit has been exceeded and the job has been terminated."""


class SoftTimeLimitExceeded(Exception):
    """The soft time limit has been exceeded. This exception is raised
    to give the task a chance to clean up."""


class WorkerLostError(Exception):
    """The worker processing a job has exited prematurely."""
