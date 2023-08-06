import os
from setuptools import setup, find_packages

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='hourglass',
    version='0.1.1',
    description='Scheduling for rq.',
    long_description=readme,
    author='Pitchfork Media, Inc.',
    author_email='dev@pitchfork.com',
    url='http://github.com/pitchfork/hourglass/',
    packages=find_packages(),
    scripts=['bin/hourglass'],
    install_requires=['rq'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
)
