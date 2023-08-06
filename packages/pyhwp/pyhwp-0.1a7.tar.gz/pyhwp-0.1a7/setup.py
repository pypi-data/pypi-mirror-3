from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata as DistMeta
    DistMeta.classifiers = None
    DistMeta.download_url = None

def read(filename):
    import os.path
    filename = os.path.join(os.path.dirname(__file__), filename)
    f = file(filename, 'r')
    try:
        return f.read()
    finally:
        f.close()

from setuptools import setup
setup(
        name='pyhwp',
        version='0.1a7',
        license='GNU Affero GPL v3',
        description = 'hwp file format parser',
        long_description=read('README'),
        author = 'mete0r',
        author_email = 'mete0r@sarangbang.or.kr',
        url='http://github.com/mete0r/pyhwp',
        packages = ['hwp5'],
        package_data = dict(hwp5=['xsl/*.xsl']),

        install_requires=['OleFileIO_PL >=0.20'],
        extras_require=dict(test=['simplejson', 'lxml']),

        entry_points = {
            'console_scripts': [
                'hwp5proc = hwp5.proc:main',
                'hwp5file = hwp5.filestructure:main',
                'unole = hwp5.filestructure:unole',
                'hwp5rec = hwp5.recordstream:main',
                'hwp5bin = hwp5.binmodel:main',
                'hwp5xml = hwp5.xmlmodel:main',
                'rawzlib = hwp5.zlib_raw_codec:main',
                'hwp5odt = hwp5.hwp5odt:main',
                'hwp5txt = hwp5.hwp5txt:main',
                ]
            },

        test_suite='hwp5.tests.test_suite',

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Affero General Public License v3',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Text Processing',
            'Topic :: Text Processing :: Filters',
            ],
        )
