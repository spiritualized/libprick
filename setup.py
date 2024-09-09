from distutils.core import setup
setup(
    name='libprick',
    packages=['libprick'],
    version='1.3.0',
    description='Python interface to the Last.FM API/website with caching support',
    url='https://github.com/spiritualized/libprick',
    download_url='https://github.com/libprick/lastfmcache/archive/v1.2.0.tar.gz',
    keywords=['pricker', 'python', 'hash', 'sha256'],
    install_requires=[
                    'av==13.0.0'
                ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.11',
    ],
)
