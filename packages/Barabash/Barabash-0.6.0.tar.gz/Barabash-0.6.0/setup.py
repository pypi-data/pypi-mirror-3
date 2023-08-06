#!/usr/bin/python

from distutils.core import setup

setup(
    name='Barabash',
    version='0.6.0',
    author='Michal Nowikowski',
    author_email='godfryd@gmail.com',
    packages=['barabash'],
    url='http://barabash.99k.org/',
    license='LICENSE.txt',
    description='Barabash, a build scripting framework.',
    long_description=open('README.rst').read(),
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Software Development :: Build Tools']
#    install_requires=['pyyaml>3.0', 'mako'],
#    entry_points = {
#        'console_scripts': [
#            'rjserver = redjack.server:main',
#            'rjagent = redjack.agent:main',
#        ]
#    }

)
