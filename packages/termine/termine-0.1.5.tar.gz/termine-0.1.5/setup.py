#from distutils.core import setup
from setuptools import setup, find_packages
from termine import __version__,__author__,__author_email__,__url__
from termine import __long_description__
setup(
    name='termine',
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    packages=find_packages(),
    scripts=['bin/termine'],
    package_data={'': ['data/*']},
    include_package_data = True,
    url=__url__,
    license='MIT and GPL-2.0',
    description='Access your Groupwise appointments from the commandline.',
    long_description=__long_description__,
    install_requires=[
        "suds >= 0.4",
        "argparse >= 1.2.1",
    ],
)
