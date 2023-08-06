from setuptools import setup, find_packages

setup(
    name='rconite',
    version='1.0',
    author='Owen Jacobson',
    author_email='owen.jacobson@grimoire.ca',
    
    description='CLI interface to Valve-style rcon servers',
    url='https://bitbucket.org/ojacobson/rconite/',
    
    packages=find_packages(),
    scripts=[
        'rcon',
    ],
)
