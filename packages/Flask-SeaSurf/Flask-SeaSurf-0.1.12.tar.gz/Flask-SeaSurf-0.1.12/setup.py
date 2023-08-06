'''
    Flask-SeaSurf
    -------------
    
    An updated cross-site forgery protection extension for Flask.

    Links
    `````

    * `documentation <http://packages.python.org/Flask-SeaSurf>`_
'''

import os
import sys

from setuptools import setup

if sys.argv[-1] == 'test':
    nosetests = 'nosetests -v --with-coverage --cover-package=flaskext'
    try:
        import yanc
        nosetests += ' --with-yanc'
    except ImportError:
        pass
    os.system('pyflakes flaskext tests; '
              'pep8 flaskext tests && '
              + nosetests)
    sys.exit()

setup(
    name='Flask-SeaSurf',
    version='0.1.12',
    url='https://github.com/maxcountryman/flask-seasurf/',
    license='BSD',
    author='Max Countryman',
    author_email='maxc@me.com',
    description='An updated CSRF extension for Flask.',
    long_description=open('README.markdown').read(),
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=['Flask'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
