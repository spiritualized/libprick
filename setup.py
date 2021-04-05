from distutils.core import setup
setup(
    name = 'libprick',
    packages = ['libprick'],
    version = '1.1.0',
    description = 'Python interface to the Last.FM API/website with caching support',
    url = 'https://github.com/spiritualized/libprick',
    download_url = 'https://github.com/libprick/lastfmcache/archive/v1.1.0.tar.gz',
    keywords = ['pricker', 'python', 'hash', 'sha256'],
    install_requires = [
                    'av==8.0.2'
                ],

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
