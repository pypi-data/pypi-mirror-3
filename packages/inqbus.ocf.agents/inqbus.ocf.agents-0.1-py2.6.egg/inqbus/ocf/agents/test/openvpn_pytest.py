import pytest

from inqbus.ocf.agents.openvpn import OpenVPN
from inqbus.ocf.generic.exits import OCF_ERR_UNIMPLEMENTED

from inqbus.ocf.agents.test import data

from inqbus.ocf.agents.test.data import pytest_generate_tests


class TestOpenvpnRun:

    scenarios = data.SCENARIO_OCFTESTER_ACTIONS_RETCODES

    def setup_method(self, method):
        self.TEST_CLASSES = [OpenVPN]

    def test_base_actions(self, action, error):
        vector = ['agent', action ]
        assert self.TEST_CLASSES[0]().run(vector) == True


#    def test_base_actions(self):
#        for action in data.BASE_ACTIONS :
#            for TestClass in self.TEST_CLASSES :
#                vector = ['agent', action ]
#                assert TestClass().run(vector) == True
#
#    def test_bad_action(self):
#        for sysargv in data.BAD_ACTIONS :
#            for TestClass in self.TEST_CLASSES :
#            # None of the bad ones may pass
#                pytest.raises(OCF_ERR_UNIMPLEMENTED, TestClass().run, sysargv)

