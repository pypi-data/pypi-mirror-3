# -*- coding: utf-8 -*-
import os
from setuptools import setup


ROOTDIR = os.path.dirname(__file__)
README = os.path.join(ROOTDIR, 'README.rst')


def run_tests():
    import sys, subprocess
    errno = subprocess.call([sys.executable, 'runtests.py'])
    raise SystemExit(errno)


setup(
    name='MailShake',
    version='0.6',
    author='Juan-Pablo Scaletti',
    author_email='juanpablo@lucumalabs.com',
    packages=['mailshake'],
    package_data={'': [
        '*.*',
        'mailshake/*.*',
        'mailshake/mailers/*.*',
        'tests/*.*',
        'docs/*.*',
    ]},
    zip_safe=False,
    url='http://github.com/lucuma/MailShake',
    license='MIT license (http://www.opensource.org/licenses/mit-license.php)',
    description='Wrappers to sending emails (or testing it) from your Python app.',
    long_description=open(README).read(),
    include_package_data=True,
    install_requires=[],
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
