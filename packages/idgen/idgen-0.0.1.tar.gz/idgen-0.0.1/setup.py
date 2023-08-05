from distutils.core import setup

setup(
    name = 'idgen',
    packages = ['idgen'],
    version = '0.0.1',
    description = 'Generate encrypted identifiers',
    author = 'Asher Blum',
    author_email = 'asher@wildsparx.com',
    url = 'http://wildsparx.com/idgen/',
    download_url = 'http://wildsparx.com/idgen/idgen-0.0.1.tar.gz',
    long_description = open("README.rst").read(),
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
        "Topic :: Text Processing :: General",
        "Topic :: Database",
    ],
)
