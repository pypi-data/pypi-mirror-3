"Python control of stepper motors."

from distutils.core import setup
import os.path

from stepper import __version__


classifiers = """\
Development Status :: 2 - Pre-Alpha
Intended Audience :: Developers
Intended Audience :: Science/Research
Operating System :: OS Independent
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

_this_dir = os.path.dirname(__file__)

setup(name='stepper',
      version=__version__,
      maintainer='W. Trevor King',
      maintainer_email='wking@tremily.us',
      url = 'http://blog.tremily.us/posts/stepper/',
      download_url = 'http://git.tremily.us/?p=stepper.git;a=snapshot;h=v{};sf=tgz'.format(
        __version__),
      license = 'GNU General Public License (GPL)',
      platforms = ['all'],
      description = __doc__.split('\n', 1)[0],
      long_description = open(os.path.join(_this_dir, 'README'), 'r').read(),
      classifiers = filter(None, classifiers.split('\n')),
      py_modules = ['stepper'],
      provides=['stepper'],
      )
