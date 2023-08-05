# -*- coding: utf-8 -*-

import os
from distutils.core import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name = 'srmqt4',
    version = '0.1',
    author = 'Alexey Zotov',
    author_email = 'alexey.zotov@gmail.com',
    url = 'http://code.google.com/p/srmqt4/',
    description = 'Linux software RAID monitoring tool',
    license = 'GPLv2',
    packages = [
        'srmqt4'
    ],
    long_description = read('README'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Topic :: System :: Monitoring'
    ],
    platforms = ['Linux'],
    package_data = {
        'srmqt4': ['ui/*.ui']
    },
    data_files = [
        (
            'bin',
            ['data/bin/srmqt4']
        ),
        (
            'share/applications',
            ['data/share/applications/softraid-monitor.desktop']
        )
    ],
    scripts = ['data/bin/srmqt4']
)
