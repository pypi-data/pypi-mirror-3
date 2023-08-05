import os
import string

from lava_test.api.core import ITest
from lava_test.core.artifacts import TestArtifacts
from lava_test.core.config import get_config


class ModuleCheck(ITest):

    @property
    def test_id(self):
        return "gatormodule"

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
        #with open(artifacts.stdout_pathname, "wt") as stream:
         #   print >>stream, random.choice(["ok", "not ok"])
        
	os.system("lsmod > lsmod.out")

	return artifacts, run_failed

    def parse(self, artifacts):
        #with open(artifacts.stdout_pathname, "rt") as stream:
            #data = stream.read().strip()

	f=open("lsmod.out")
	data=f.read()

        return {
            "test_results": [
                {
                    "test_case_id": "modulecheck",
                    "log_filename": artifacts.stdout_pathname,
                    "log_lineno": 1,
                    "result": "fail" if string.find(data,"gator") == -1 else "pass",
                    "message": "lsmod output was %r" % data
                }
            ]
        }


testobj = ModuleCheck()
