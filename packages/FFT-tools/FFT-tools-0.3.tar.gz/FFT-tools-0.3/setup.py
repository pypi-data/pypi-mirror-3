"Wrap NumpPy's FFT routines to reduce clutter."

from distutils.core import setup
import os.path

from FFT_tools import __version__


package_name = 'FFT-tools'
_this_dir = os.path.dirname(__file__)

setup(name=package_name,
      version=__version__,
      maintainer='W. Trevor King',
      maintainer_email='wking@tremily.us',
      url = 'http://blog.tremily.us/posts/{}/'.format(package_name),
      download_url = 'http://git.tremily.us/?p={}.git;a=snapshot;h={};sf=tgz'.format(package_name, __version__),
      license = 'GNU General Public License (GPL)',
      platforms = ['all'],
      description = __doc__,
      long_description = open(os.path.join(_this_dir, 'README'), 'r').read(),
      classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      py_modules = ['FFT_tools'],
      )
