import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pysprints',
    version='1.0.2',
    author='Mark Henwood',
    author_email='mark@mcbh.co.uk',
    description='Sprint / Release planning objects',
    license='MIT',
    keywords='sprint agile scrum project',
    url='http://pypi.python.org/pypi/pysprints',
    packages=['pysprints'],
    provides=['pysprints'],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: Utilities'
    ]
)
