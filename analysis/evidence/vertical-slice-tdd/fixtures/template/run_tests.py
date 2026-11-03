import json
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = ROOT / ".testlog.jsonl"


def log(test, outcome):
    with LOG.open("a") as handle:
        handle.write(json.dumps({
            "test": str(test),
            "outcome": outcome,
            "time": time.time(),
        }) + "\n")


class LoggingResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        log(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        log(test, "failed")

    def addError(self, test, err):
        super().addError(test, err)
        log(test, "error")


def main():
    log("session", "start")
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=2, resultclass=LoggingResult).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
