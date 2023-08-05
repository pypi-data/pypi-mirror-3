# -*- coding: utf-8 -*-
import os
from setuptools import setup


README = os.path.join(os.path.dirname(__file__), 'README.rst')

def run_tests():
    import sys, subprocess
    errno = subprocess.call([sys.executable, 'runtests.py'])
    raise SystemExit(errno)


setup(
    name='Clay',
    version='0.8',
    author='Juan-Pablo Scaletti',
    author_email='juanpablo@lucumalabs.com',
    packages=['clay'],
    package_data={'clay': [
            '*.*',
            'processors/*.*',
            'extensions/*.*',
            'libs/*.*',
            'skeleton/.gitignore',
            'skeleton/*.*',
            'skeleton/views/*.*',
            'skeleton/views/static/*.*',
            'skeleton/views/static/images/*.*',
            'skeleton/views/static/scripts/*.*',
            'skeleton/views/static/styles/*.*',
            'tests/*.*',
            'tests/views/*.*',
            'tests/views/foo/*.*',
            'views/*.*',
        ]},
    zip_safe=False,
    url='http://github.com/lucuma/Clay',
    license='MIT license (http://www.opensource.org/licenses/mit-license.php)',
    description='A rapid prototyping tool',
    long_description=open(README).read(),
    install_requires=[
        'Shake>=0.21',
        # 'Markdown',
        # 'Pygments',
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
    entry_points="""
    [console_scripts]
    clay = clay.manage:main
    """
)
