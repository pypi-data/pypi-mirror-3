import os

from inqbus.ocf.agents.pidbaseagent import PIDBaseAgent
from inqbus.ocf.generic import parameter, exits
from subprocess import Popen


class PIDAgent(PIDBaseAgent):
    """
    Agent for arbitrary executable controlled by a explicitly given PIDfile. 
    """

    def config(self):
        """
        Configure the OCF Paramters: executable and pid_file.
        """
        # Do not forget to call the inherited method!
        super(PIDAgent, self).config()
        # Paramter 'excecutable'
        self.params["executable"] = parameter.OCFString(
          longdesc="""Path to the executable""",
          shortdesc="executable",
          required=True,
          validate=PIDAgent.validate_executable) # Note the validation function
        # Paramter 'pid_file'
        self.params["pid_file"] = parameter.OCFString(
          longdesc="""Path to the pid file""",
          shortdesc="pid file",
          required=True)

    def get_pid_file(self):
        """
        Tell where the PIDFile is to be faound
        """
        return self.params.pid_file.value

    def get_executable(self):
        """
        Tell where the executable is to be faound
        """
        return self.params.executable.value

    def start_process(self):
        """
        Start the executable.
        """
        # Construct the comanndline vector
        args = [ self.params.executable.value, self.pid_file]
        # intitialize the process
        proc = Popen(args)
        # check if we can communicate with the process
        res = proc.communicate()
        # If we cannot reach the process ..
        if proc.returncode != 0 :
            #  .. we are not able to start it.
            raise exits.OCF_NOT_RUNNING("start: canot start the process %s" % args)

def main():
    """
    Entry point for the python console scripts
    """
    import sys
    PIDAgent().run(sys.argv)

if __name__ == "__main__":
    main()
