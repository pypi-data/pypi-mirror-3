#!/usr/bin/python

"""
Pre-alpha Command-Line Interface for PiCloud.

For Linux, need to install /usr/bin/picloud with contents:

#!/usr/bin/python

import cloud
import cloud.cli
cloud.cli.main()


TBD what to do for Windows.
"""

import sys

def main():
    
    args = sys.argv[:]
    args.pop(0)
    
    sub_module = args.pop(0)
    module_func = args.pop(0)
    
    module_name = 'cloud.%s' % sub_module
    
    if module_name not in sys.modules:
        raise Exception('Invalid Command')
    
    func = getattr(sys.modules[module_name], module_func)
    
    res = func(*args)
    if res:
        print res
    