import nose.tools

import os

from inqbus.ocf.agents.pidagent import PIDAgent

from inqbus.ocf.agents.test import data
#from test_openvpn import TestOpenvpnRunBase

TEST_CLASSES = [PIDAgent]


class TestPidagentWithDummyDaemon():
    def setUp(self):
        """
        Use the dummy_daemon
        """
        os.environ['OCF_RESKEY_pid_file'] = '/tmp/dummy_daemon.pid'
        os.environ['OCF_RESKEY_executable'] = './bin/dummy_daemon'

    def test_ocftester_actions(self):
        self.TEST_CLASSES = TEST_CLASSES
        for TestClass in self.TEST_CLASSES :
            for action, error in data.OCFTESTER_ACTIONS_RETCODES :
                vector = ['agent', action ]
                yield self.do_ocftester_actions, TestClass, vector, error

    def do_ocftester_actions(self, TestClass, vector, error):
        self.TEST_CLASSES = TEST_CLASSES
        if not error :
            assert TestClass().run(vector) == True
        else :
            nose.tools.assert_raises(error, TestClass().run, vector)
