long_description = open('README.txt').read()

from setuptools import setup, find_packages

requires = []

setup(
    name='bigbluebutton',
    version='0.3.0',
    author='Reimar Bauer',
    maintainer='Reimar Bauer',
    maintainer_email='rb.proj@googlemail.com',
    url='https://bitbucket.org/ReimarBauer/bigbluebutton-python-api',
    description='API for bigbluebutton.',
    long_description=long_description,
    keywords='bigbluebutton',
    license='MIT',
    packages=find_packages(),
    install_requires=requires,
)
