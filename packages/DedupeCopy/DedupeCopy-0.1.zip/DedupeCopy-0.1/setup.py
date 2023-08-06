from distutils.core import setup

setup(
    name='DedupeCopy',
    version='0.1',
    author='Erik Schweller',
    author_email='othererik@gmail.com',
    packages=['dedupe_copy', 'dedupe_copy.test', ],
    url='http://pypi.python.org/pypi/DedupeCopy/',
    download_url='http://www.bitbucket.org/othererik/dedupe_copy',
    scripts=['dedupe_copy/dedupe_copy.py', ],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    description='Find duplicates / copy and restructure file layout '
        'command-line tool',
    platforms=['any'],
    keywords=['de-duplication',
        'file management',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
)
