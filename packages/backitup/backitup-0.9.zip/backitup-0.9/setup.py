from setuptools import setup

setup(
    name = 'backitup',
    version = '0.9',
    author = 'Rob Galanakis',
    author_email = 'rob.galanakis@gmail.com',
    url = 'http://code.google.com/p/backitup/',

    packages = ['backitup'],

    description = 'Simply library for easily customized backup and uploading of your files',
    long_description = open('README.txt').read(),

    license = "MIT",
    platforms = ['POSIX', 'Windows'],
    keywords = ['encoding', 'i18n', 'xml'],
    classifiers = [
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",

        "Topic :: Software Development :: Libraries :: Python Modules",
        'Topic :: System :: Archiving',
        'Topic :: System :: Archiving :: Backup',

        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators'
        ],
    )
