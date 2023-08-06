import sys
import os.path
from setuptools import setup, find_packages

readme = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(readme).read()

setup(
    name='vcsdeploy',
    version='0.2',
    author='Antonio Cuni',
    author_email='anto.cuni@gmail.com',
    packages=['vcsdeploy'],
    url='http://bitbucket.org/antocuni/vcsdeploy',
    license='BSD',
    description='Minimal GUI to deploy updates through a VCS repository',
    long_description=long_description,
    keywords='deployment vcs mercurial GUI',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Topic :: System :: Installation/Setup",
        ],
    install_requires=['py'], # and also PyQT, but it doesn't work with
                             # setuptools :-(
)
