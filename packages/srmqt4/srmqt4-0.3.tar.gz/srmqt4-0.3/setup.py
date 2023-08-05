# -*- coding: utf-8 -*-

import os
from distutils.core import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

VERSION = '0.3'

setup(
    name = 'srmqt4',
    version = VERSION,
    author = 'Alexey Zotov',
    author_email = 'alexey.zotov@gmail.com',
    url = 'http://code.google.com/p/srmqt4/',
    description = 'Linux software RAID monitoring tool',
    license = 'GPLv2',
    packages = [
        'srmqt4'
    ],
    long_description = read('README'),
    download_url = 'http://srmqt4.googlecode.com/files/srmqt4-%s.tar.gz' % VERSION,
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
    requires = [
        'PyQt4 (>=4.0)'
    ],
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
