# -*- coding: utf-8 -*-
'''setup - setuptools based setup for shove.'''

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='shove',
    version='0.3.4',
    description='''Common object storage frontend''',
    long_description=open('README.rst').read(),
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    url='http://pypi.python.org/pypi/shove/',
    license='BSD',
    packages=['shove', 'shove.cache', 'shove.store', 'shove.tests'],
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
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points='''
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
