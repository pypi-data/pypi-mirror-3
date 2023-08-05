import nose.tools

import os
import shutil
import tempfile


from inqbus.ocf.agents.pidbaseagent import PIDBaseAgent
from inqbus.ocf.generic.exits import OCF_ERR_PERM

class Param(object):
            """
            Class mocking inqbus.ocf.generig.parameter.OCFType
            """
            def __init__(self, value):
                self.value = value

TEST_CLASSES = [PIDBaseAgent]


class TestPidBaseAgent(object):
    def setUp(self):
        """
        Build a config Directory and a file
        """
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = tempfile.mkstemp(dir=self.temp_dir)[1]

    def tearDowm(self):
        """
        Remove the temp_dir recursively
        """
        shutil.rmtree(self.temp_dir)

    def test_validator_good_dir(self):
        self.TEST_CLASSES = TEST_CLASSES
        for TestClass in self.TEST_CLASSES :
            agent = TestClass()
            param_dir = Param(self.temp_dir)
            agent.validate_dir(param_dir)

    def test_validator_bad_dir(self):
        self.TEST_CLASSES = TEST_CLASSES
        for TestClass in self.TEST_CLASSES :
            agent = TestClass()
            # changing dirname 
            param_dir = Param(self.temp_dir + 'XXXX')
            error = OCF_ERR_PERM
            nose.tools.assert_raises(error, agent.validate_dir, param_dir)

    def test_validator_noread_dir(self):
        self.TEST_CLASSES = TEST_CLASSES
        for TestClass in self.TEST_CLASSES :
            agent = TestClass()
            # removing read permission
            param_dir = Param(self.temp_dir + 'XXXX')
            os.chmod(self.temp_dir, 0o333)
            error = OCF_ERR_PERM
            nose.tools.assert_raises(error, agent.validate_dir, param_dir)

    def test_validator_good_file(self):
        self.TEST_CLASSES = TEST_CLASSES
        for TestClass in self.TEST_CLASSES :
            agent = TestClass()
            param_file = Param(self.temp_file)
            agent.validate_file(param_file)

    def test_validator_bad_file(self):
        self.TEST_CLASSES = TEST_CLASSES
        for TestClass in self.TEST_CLASSES :
            agent = TestClass()
            # changing filename
            param_file = Param(self.temp_file + 'XXXX')
            error = OCF_ERR_PERM
            nose.tools.assert_raises(error, agent.validate_file, param_file)

    def test_validator_noread_file(self):
        self.TEST_CLASSES = TEST_CLASSES
        for TestClass in self.TEST_CLASSES :
            agent = TestClass()
            # removing read permission
            param_file = Param(self.temp_file)
            os.chmod(self.temp_file, 0o333)
            error = OCF_ERR_PERM
        if os.geteuid() != 0:
            nose.tools.assert_raises(error, agent.validate_file, param_file)


    def test_validator_good_executable(self):
        self.TEST_CLASSES = TEST_CLASSES
        for TestClass in self.TEST_CLASSES :
            agent = TestClass()
            param_file = Param(self.temp_file)
            # setting execute permission
            os.chmod(self.temp_file, 0o700)
            agent.validate_executable(param_file)

    def test_validator_bad_executable(self):
        self.TEST_CLASSES = TEST_CLASSES
        for TestClass in self.TEST_CLASSES :
            agent = TestClass()
            param_file = Param(self.temp_file)
            # changing filename
            param_file = Param(self.temp_file + 'XXXX')
            error = OCF_ERR_PERM
            nose.tools.assert_raises(error, agent.validate_executable, param_file)

    def test_validator_noexec_executable(self):
        self.TEST_CLASSES = TEST_CLASSES
        for TestClass in self.TEST_CLASSES :
            agent = TestClass()
            param_file = Param(self.temp_file)
            # removing execute permission
            os.chmod(self.temp_file, 0o666)
            error = OCF_ERR_PERM
            nose.tools.assert_raises(error, agent.validate_executable, param_file)

