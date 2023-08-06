import os.path
import sys
import subprocess

from distutils.core import setup
from distutils.command.install import install
from distutils.errors import DistutilsExecError

import os.path

def get_omniorb_cos_path():
    pkg_config = subprocess.Popen(['pkg-config',
                                   '--variable=idldir',
                                   'omniCOS4'],
                                  stdout=subprocess.PIPE)
    (out, err) = pkg_config.communicate()

    if pkg_config.returncode != 0:
        raise EnvironmentError('Can''t find where to look for TimeBase.idl!')

    return out.rstrip()

def compile_idl(filenames, includes, outputdir):
    # This is Debian specific
    if os.path.isdir('/usr/lib/omniidl'):
        sys.path.append('/usr/lib/omniidl')

    for filename in filenames:
        print 'compiling %s into %s' % (filename, outputdir)

        try:
            import _omniidl
            import omniidl.main
            omniidl.main.main(['ignored', '-bpython'] +
                              ['-I' + path for path in includes] +
                              ['-C' + outputdir, filename])
        except ImportError, e:
            raise DistutilsExecError('omniidl not available')

class generate_corba_stubs(install):
    def run(self):
        install.run(self)
        compile_idl(['DsLogAdmin.idl', 'DsEventLogAdmin.idl', 'DsNotifyLogAdmin.idl'],
                    [get_omniorb_cos_path(), '.'],
                    self.install_lib)

setup(
    name='tlscli',
    version='1.0.1',
    author='Thomas Girard',
    author_email='thomas.g.girard@free.fr',
    url='https://launchpad.net/tlscli',
    license='LICENSE.txt',
    description='Text User Interface client for CORBA Telecom Log Service.',
    long_description=open('README.txt').read(),
    scripts=['tlscli'],
    cmdclass={'install': generate_corba_stubs},
    requires=['dateutil.parser'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ]
)
