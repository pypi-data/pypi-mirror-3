from __future__ import print_function

import os
import shutil
import sys
import tempfile

import nose.tools
from nose.plugins.skip import SkipTest

from inqbus.ocf.agents.openvpn import OpenVPN
from inqbus.ocf.generic.exits import OCF_ERR_UNIMPLEMENTED

from inqbus.ocf.agents.test import data

def setup_module():
    """
    Installing valid filesystem information so the validation of the paramters will pass.
    """
    global temp_dir
    ovpn_name = 'test' # name of the openvpn instane
    temp_dir = tempfile.mkdtemp() # temporary directory
    # A config file derived from the instance name
    conf_file_name = os.path.join(temp_dir, '%s.conf' % ovpn_name)
    log_file_name = os.path.join(temp_dir, '%s.log' % ovpn_name)
    stat_file_name = os.path.join(temp_dir, '%s.status' % ovpn_name)
    secret_file_name = os.path.join(temp_dir, '%s.sec' % ovpn_name)
    conf_file = open(conf_file_name, 'w')
    conf_file.write(
"""
local 127.0.0.1
port 1194
proto udp
dev tun

#server 128.0.0.0 255.255.255.0
persist-tun
status %s
log-append %s
secret %s
verb 0
""" % (stat_file_name, log_file_name, secret_file_name))
    conf_file.close()

    secret_file = open(secret_file_name, 'w')
    secret_file.write(
"""
#
# 2048 bit OpenVPN static key
#
-----BEGIN OpenVPN Static key V1-----
4ec99f2e9c12e1128fbfa9b3634cecfe
be36c1868342232a9c3332049e8c6a5d
cb98b91ff04a522d4ea6e59e481be70d
38bdead8607fc9367a1d8b7d1d558164
2ffa1e377f48685cf3cdfcaeef639d21
2ff9c6570127d34c57c6dc0e6ad1677b
f7f9fb15d0244b5de0a0e71083089dde
0e224ab5b2171a32a120a8735c9be7de
df277a7d90c34bcf323005f33d7fb8e7
3766888f3a18529059e6d7666179861a
a7c9119d0ef908cd45af2dcca94190fb
09624ac49130494e1fc72fa0d2378ba2
8e89f0754355742bbfd020730238cb15
20097756e1404de3b388f026b30d6697
34f232afc77004b890e8f9a945feaa81
641264b6c03669a1c67bd7d1098adc90
-----END OpenVPN Static key V1-----
""")
    secret_file.close()

    os.environ['OCF_RESKEY_ovpn_conf_dir'] = temp_dir
    os.environ['OCF_RESKEY_ovpn_name'] = ovpn_name
    os.environ['OCF_RESKEY_ovpn_pid_dir'] = temp_dir
    os.environ['OCF_RESKEY_ovpn_run_dir'] = temp_dir

def teardown():
    """
    Remove the temp_dir recursively. Remove the environamt parameters
    """
    global temp_dir
    shutil.rmtree(temp_dir)
    del os.environ['OCF_RESKEY_ovpn_conf_dir']
    del os.environ['OCF_RESKEY_ovpn_name']
    del os.environ['OCF_RESKEY_ovpn_pid_dir']
    del os.environ['OCF_RESKEY_ovpn_run_dir']

class TestOpenvpnRunBase():
    """
    Test the basic actions 
    """

    # Test the if buildin actions: validate-all, meta-data pass
    def test_base_actions(self):
        self.TEST_CLASSES = [OpenVPN]
        for TestClass in self.TEST_CLASSES:
            for sysargv in data.BASE_ACTIONS :
                yield self.do_good_action, TestClass, sysargv

    def do_good_action(self, TestClass, sysargv):
        """
        worker function for test_good_actions
        """
        assert TestClass().run(sysargv) == True

    def test_bad_actions(self):
        """
        Test if invalid actions do fail: 
        """
        self.TEST_CLASSES = [OpenVPN]
        for TestClass in self.TEST_CLASSES:
            for sysargv in data.BAD_ACTIONS :
                yield self.do_bad_action, TestClass, sysargv

    def do_bad_action(self, TestClass, sysargv):
        """
        worker function for test_bad_actions
        """
        nose.tools.assert_raises(OCF_ERR_UNIMPLEMENTED, TestClass().run, sysargv)

class TestOpenvpnRunOCFtester():
    """
    Test the OCFTester actions 
    """
    def setUp(self):
        if os.geteuid() != 0 :
            raise SkipTest("This test can only be run by root")

    # Run a complete OCFtester actions set against the openvpn agent
    def test_ocftester_actions(self):
        self.TEST_CLASSES = [OpenVPN]
        for TestClass in self.TEST_CLASSES:
            for action, error in data.OCFTESTER_ACTIONS_RETCODES:
                yield self.do_ocftester_action, TestClass, action, error

    def do_ocftester_action(self, TestClass, action, error):
        """
        worker function for test_ocftester_actions
        """
        vector = ['agent', action ]
        if not error :
            assert TestClass().run(vector) == True
        else :
            nose.tools.assert_raises(error, TestClass().run, vector)


