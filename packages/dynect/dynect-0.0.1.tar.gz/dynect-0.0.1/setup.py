from setuptools import setup, find_packages
from os.path import join, abspath, dirname
here = lambda *x: join(abspath(dirname(__file__)), *x)


setup(
    name='dynect',
    version='0.0.1',
    description='Wrapper library to Dynect API.',
    long_description=here('README.rst'),
    author='Jorge Eduardo Cardona',
    author_email='jorgeecardona@gmail.com',
    test_requires=['unittest2'],
    test_suite='tests')
