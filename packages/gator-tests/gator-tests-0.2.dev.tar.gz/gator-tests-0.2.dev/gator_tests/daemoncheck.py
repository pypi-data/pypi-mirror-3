import os
import string

from lava_test.api.core import ITest
from lava_test.core.artifacts import TestArtifacts
from lava_test.core.config import get_config


class DaemonCheck(ITest):
    		
    
    @property
    def test_id(self):
        return "gatordaemon"

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


	gatord_out = os.system("gatord > gatord.out 2>&1")

        with open(artifacts.stdout_pathname, "wt") as stream:
            print >>stream, gatord_out        

	return artifacts, run_failed

    def parse(self, artifacts):
        with open(artifacts.stdout_pathname, "rt") as stream:
            error_level = stream.read().strip()

	f=open("gatord.out")
	gatordout=f.read()

        return {
            "test_results": [
                {
                    "test_case_id": "daemoncheck",
                    "log_filename": artifacts.stdout_pathname,
                    "log_lineno": 1,
                    "result": "pass" if error_level == '0' else "fail",
                    "message": "gatord output was %r" % gatordout
		    	
                }
            ]
        }


testobj = DaemonCheck()
