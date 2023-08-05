import random

from lava_test.api.core import ITest
from lava_test.core.artifacts import TestArtifacts
from lava_test.core.config import get_config


class DemoTest(ITest):

    @property
    def test_id(self):
        return "demo"

    @property
    def is_installed(self):
        return True

    def install(self, observer):
        pass

    def uninstall(self, observer):
        pass

    def run(self, observer, test_options):
        config = get_config()
        artifacts = TestArtifacts.allocate(self.test_id, config)
        run_failed = False
        with open(artifacts.stdout_pathname, "wt") as stream:
            print >>stream, random.choice(["ok", "not ok"])
        return artifacts, run_failed

    def parse(self, artifacts):
        with open(artifacts.stdout_pathname, "rt") as stream:
            data = stream.read().strip()
        return {
            "test_results": [
                {
                    "test_case_id": "random-choice",
                    "log_filename": artifacts.stdout_pathname,
                    "log_lineno": 1,
                    "result": "pass" if data == "ok" else "fail",
                    "message": "Random data was %r" % data
                }
            ]
        }


testobj = DemoTest()
