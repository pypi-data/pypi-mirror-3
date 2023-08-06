import sys
import time
from itertools import count

from billiard.einfo import ExceptionInfo


def maybe_leak(i):
    try:
        raise KeyError(i)
    except KeyError:
        einfo = ExceptionInfo(sys.exc_info())
        return einfo


for i in count():
    maybe_leak(i)
    if i % 10000000:
        print(i)
        time.sleep(1)
