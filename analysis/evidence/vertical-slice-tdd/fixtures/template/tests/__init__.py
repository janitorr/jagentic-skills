"""Log unittest outcomes for eval runs, including direct `python3 -m unittest`."""
import json
import time
import unittest
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / ".testlog.jsonl"


def _log(test, outcome):
    with LOG.open("a") as handle:
        handle.write(json.dumps({
            "test": str(test),
            "outcome": outcome,
            "time": time.time(),
        }) + "\n")


class _LoggingResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        _log(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        _log(test, "failed")

    def addError(self, test, err):
        super().addError(test, err)
        _log(test, "error")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        _log(test, "skipped")


_original_init = unittest.TextTestRunner.__init__


def _init(self, *args, **kwargs):
    kwargs.setdefault("resultclass", _LoggingResult)
    _original_init(self, *args, **kwargs)


unittest.TextTestRunner.__init__ = _init
