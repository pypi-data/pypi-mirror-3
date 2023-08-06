
import sys, os, subprocess
from ctypes import windll
mbox = windll.user32.MessageBoxA

python_install_dir = sys.prefix
setuptools_exe = os.path.join(python_install_dir, 'Scripts\distribute-0.6.26.win32.msi')
exe_path = os.path.join(python_install_dir, 'Scripts\picloud.exe')

try:
    import pkg_resources
except ImportError:
    ret_value = subprocess.call(['msiexec', '/i', setuptools_exe, '/quiet'])
    if ret_value != 0:
        mbox(None, 'Setuptools installation failed.\nPicloud not installed!\nAborting installation.', 'Installation error', 16)
        exit(1)

finish_string = ''
try:
    import cloud
    if cloud.config.api_key == 'None':
        result = subprocess.call( [exe_path, 'setup'] )
    else:
        result = 0

except ImportError:
    result = -1

if result == 0:
    finish_string = "PiCloud is successfully installed and setup."
elif result == -1:
    finish_string = "PiCloud is installed successfully, but there was a problem in setup.\n\nPlease run \n\n  %s setup \n\nfrom command line to complete setup" % exe_path
else:
    finish_string = "PiCloud is installed successfully, but there was a problem in setup:\nThe email address and the password did not match.\n\nPlease run \n\n  %s setup \n\nfrom command line to complete setup" % exe_path

# mbox(None, finish_string, 'Installation Success', 0)
sys.stderr.write(finish_string)