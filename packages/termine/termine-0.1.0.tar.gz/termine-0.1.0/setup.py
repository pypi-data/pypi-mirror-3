from distutils.core import setup

setup(
    name='termine',
    version='0.1.0',
    author='Ciaran Farrell',
    author_email='cfarrell1980@gmail.com',
    packages=['termine'],
    scripts=['bin/termine'],
    url='http://bitbucket.org/cfarrell1980/termine/',
    license='LICENSE.txt',
    description='Access your Groupwise appointments from the commandline.',
    long_description=open('README.txt').read(),
    install_requires=[
        "suds >= 0.4",
        "argparse >= 1.2.1",
    ],
)
