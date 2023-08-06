try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='PlayingCards',
    version='0.1.2',
    author='Paritosh Mathur',
    author_email='admin@parrymathur.com',
    packages=['playingcards','playingcards.test'],
    scripts=['bin/interface.py'],
    url='',
    license='LICENSE.txt',
    description='A module to create card games and playing card simulations.',
    long_description=open('README.txt').read(),
    install_requires=[],
    )
