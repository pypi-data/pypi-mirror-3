# Copyright (c) 2006-2011 L. C. Rees.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 3.  Neither the name of the Portable Site Information Project nor the names
# of its contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''setup - setuptools based setup for shove.'''

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='shove',
    version='0.3.3',
    description='''Common object storage frontend''',
    long_description=open('README.rst').read(),
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    url='http://pypi.python.org/pypi/shove/',
    license='BSD',
    packages = ['shove', 'shove.cache', 'shove.store', 'shove.tests'],
    py_modules=['ez_setup'],
    test_suite='shove.tests',
    zip_safe=False,
    keywords='object storage persistence database shelve',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
    ],
    entry_points = '''
    [shove.stores]
    bsddb=shove.store.bsdb:BsdStore
    dbm=shove.store.dbm:DbmStore
    durus=shove.store.durusdb:DurusStore
    file=shove.store.file:FileStore
    firebird=shove.store.db:DbStore
    ftp=shove.store.ftp:FtpStore
    memory=shove.store.memory:MemoryStore
    mssql=shove.store.db:DbStore
    mysql=shove.store.db:DbStore
    oracle=shove.store.db:DbStore
    postgres=shove.store.db:DbStore
    simple=shove.store.simple:SimpleStore
    sqlite=shove.store.db:DbStore
    s3=shove.store.s3:S3Store
    svn=shove.store.svn:SvnStore
    zodb=shove.store.zodb:ZodbStore
    redis=shove.store.redisdb:RedisStore
    cassandra=shove.store.cassandra:Cassandra
    [shove.caches]
    bsddb=shove.cache.bsdb:BsdCache
    file=shove.cache.file:FileCache
    filelru=shove.cache.filelru:FileLRUCache
    firebird=shove.cache.db:DbCache
    memcache=shove.cache.memcached:MemCached
    memlru=shove.cache.memlru:MemoryLRUCache
    memory=shove.cache.memory:MemoryCache
    mssql=shove.cache.db:DbCache
    mysql=shove.cache.db:DbCache
    oracle=shove.cache.db:DbCache
    postgres=shove.cache.db:DbCache
    simple=shove.cache.simple:SimpleCache
    simplelru=shove.cache.simplelru:SimpleLRUCache
    sqlite=shove.cache.db:DbCache
    '''
)
