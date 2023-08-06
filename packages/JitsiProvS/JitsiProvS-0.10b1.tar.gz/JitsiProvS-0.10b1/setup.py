from setuptools import setup, find_packages
from glob import glob
import re
__version__ = re.search("__version__\s*=\s*'(.*)'", open('jitsiprovs/__init__.py').read(), re.M).group(1)
assert __version__

def read(fname):
    import os
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='JitsiProvS',
    version=__version__,
    description='Jitsi Provisioning Server',
    author='Dan-Cristian Bogos',
    author_email='dan@itsyscom.com',
    url='http://www.itsyscom.com',
    packages=find_packages(),
    data_files=[ ('scripts', glob('scripts/*')) ],
    long_description=read('README.txt'),
    classifiers=[
      "Development Status :: 4 - Beta",
      "License :: OSI Approved :: GNU General Public License (GPL)",
      "Programming Language :: Python",
      "Intended Audience :: Telecommunications Industry",
      "Development Status :: 1 - Planning",
      "Topic :: Internet",
      "Operating System :: OS Independent",
     ],
     keywords='telecommunications voip',
     license='GPLv3',
             install_requires=['python-daemon', 'sqlobject', 'flask']
    )

