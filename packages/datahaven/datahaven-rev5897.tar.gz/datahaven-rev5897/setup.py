from distutils.core import setup

setup(  

        name='datahaven',
        version='rev5897',
        author='DataHaven.NET LTD',
        author_email='build@datahaven.net',
        maintainer='Veselin Penev',
        maintainer_email='penev.veselin@gmail.com',
        url='http://datahaven.net',
        description='Distributed encrypted backup utility',
        long_description='Distributed encrypted backup utility',
        download_url='http://datahaven.net/download.html',
        #download_url='http://pypi.python.org/packages/source/d/datahaven/datahaven-rev5897.tar.gz',
        
        classifiers=[
            'Topic :: Internet',
            'Topic :: Security',
            'Topic :: Utilities',
            'Environment :: Web Environment',
            'Framework :: Twisted',
            'Development Status :: 3 - Alpha',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'Programming Language :: Python',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            ],
            
        packages=[
            'datahaven',
    		'datahaven.p2p', 
    		'datahaven.forms',
       		'datahaven.lib',
    		'datahaven.lib.shtoom',
    		'datahaven.epsilon',
    		'datahaven.vertex',
    		'datahaven.cspace',
    		'datahaven.cspace.dht',
    		'datahaven.cspace.ext',
    		'datahaven.cspace.main',
    		'datahaven.cspace.network',
    		'datahaven.cspace.util',
    		'datahaven.cspaceapps',
    		'datahaven.nitro',
		    ],
		    
)




