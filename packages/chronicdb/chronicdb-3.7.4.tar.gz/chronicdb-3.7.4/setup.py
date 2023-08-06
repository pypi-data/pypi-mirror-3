#
# Copyright (C) LoomCM 2010 for ChronicDB
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from setuptools import setup

setup( name                = 'chronicdb',
       version             = '3.7.4',
       author              = 'ChronicDB',
       author_email        = 'support@chronicdb.com',
       url                 = 'http://chronicdb.com',
       description         = 'The ChronicDB command-line client.',
       long_description    = 'ChronicDB offers live database version control.',
       package_dir         = { 'chronicdb': '.' },
       package_data        = { 'chronicdb': [ '*.crt' ] },
       packages            = [ 'chronicdb' ],
       zip_safe            = False,
       license             = 'GNU General Public License (GPL)',
       classifiers         = [ 'Environment :: Console',
                               'Intended Audience :: Developers',
                               'Intended Audience :: Financial and Insurance Industry',
                               'Intended Audience :: Healthcare Industry',
                               'Intended Audience :: Information Technology',
                               'Intended Audience :: System Administrators',
                               'Intended Audience :: Science/Research',
                               'Programming Language :: Python',
                               'Programming Language :: Python :: 3',
                               'Topic :: Database',
                               'Topic :: Database :: Database Engines/Servers',
                               'Topic :: Software Development :: Version Control',
                               'License :: OSI Approved :: GNU General Public License (GPL)',
                               'Operating System :: OS Independent' ],
       requires            = [ 'simplejson' ],
       scripts             = [ 'chd', 'chronicdb' ]
       )
