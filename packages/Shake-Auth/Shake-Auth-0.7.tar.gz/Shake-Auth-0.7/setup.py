# -*- coding: utf-8 -*-
"""
    :Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    :MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
import os
from setuptools import setup


ROOTDIR = os.path.dirname(__file__)
README = os.path.join(ROOTDIR, 'README.md')


def run_tests():
    import sys, subprocess
    errno = subprocess.call([sys.executable, 'run_tests.py'])
    raise SystemExit(errno)


setup(
    name='Shake-Auth',
    version='0.7',
    author='Juan-Pablo Scaletti',
    author_email='juanpablo@lucumalabs.com',
    packages=['shake_auth'],
    package_data={
        'shake_auth': [
            'views/*.*',
        ]
    },
    zip_safe=False,
    url='http://github.com/lucuma/Shake-Auth',
    license='MIT license (http://www.opensource.org/licenses/mit-license.php)',
    description="Shake's awesome authentication extension.",
    long_description=open(README).read(),
    include_package_data=True,
    install_requires=[
        'Shake-SQLAlchemy'
        ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='__main__.run_tests',
)
