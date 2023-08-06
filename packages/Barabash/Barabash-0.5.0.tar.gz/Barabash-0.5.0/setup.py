#!/usr/bin/python

from distutils.core import setup

setup(
    name='Barabash',
    version='0.5.0',
    author='Michal Nowikowski',
    author_email='godfryd@gmail.com',
    packages=['barabash'],
    include_package_data=True,
    url='http://barabash.99k.org/',
    license='LICENSE.txt',
    description='Barabash, a build scripting framework.',
    long_description=open('README.rst').read()#,
#    install_requires=['pyyaml>3.0', 'mako'],
#    entry_points = {
#        'console_scripts': [
#            'rjserver = redjack.server:main',
#            'rjagent = redjack.agent:main',
#        ]
#    }

)
