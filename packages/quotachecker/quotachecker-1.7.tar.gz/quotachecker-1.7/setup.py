import codecs
import os
import sys

from setuptools import Command, find_packages, setup

# If you change this version, please change it allso in "CHANGES.txt"
version = '1.7'


if sys.version_info < (2, 7):
    requirements = ["argparse"]
else:
    requirements = []


class PyTest(Command):
    description = 'Runs the test suite.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


def read(*path):
    basepath = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(basepath, *path), 'r', 'utf-8').read()


# package description
desc = "Return the quota of 1st level sub folders in a directory."
long_desc = '\n\n'.join(read(f) for f in ('README.txt', 'CHANGES.txt'))


setup(name='quotachecker',
    version=version,
    description=desc,
    long_description=long_desc,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Inqbus GmbH & Co. KG',
    author_email='info@inqbus.de',
    maintainer='Frank Schneider',
    maintainer_email='frank.schneider@inqbus.de',
    url='https://bitbucket.org/inqbus/quotachecker',
    download_url='http://pypi.python.org/pypi/quotachecker',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples']),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    entry_points=dict(console_scripts=[
        'qchecker=quotachecker:main',
        'qchecker-%s=quotachecker:main' % sys.version[:3]
    ]),
    cmdclass = {'test': PyTest},
)
