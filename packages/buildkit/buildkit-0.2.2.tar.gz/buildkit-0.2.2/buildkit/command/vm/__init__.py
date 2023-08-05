"""\
Manage virtual machines
"""

import os
from buildkit import stacks

arg_specs = []
child_command_specs = stacks.find_commands(__package__, os.path.dirname(__file__))
help_template = stacks.main_help_template + """

You can start a virtual machine using the buildkit-vm-start command. 
For example:

   buildkit-vm-start eth0 qtap0 512M 4 tmpKfAdeU.qcow2 [extra args to KVM]
"""

def run(cmd):
    return 0

