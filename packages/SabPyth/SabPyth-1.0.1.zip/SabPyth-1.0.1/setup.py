#!/usr/local/bin/python
from distutils.core import setup, Extension

SABLOTRON_DIR = 'src/Sablot-1.0.3/'
EXPAT_DIR = 'src/expat-2.1.0/lib/'

setup(
    name='SabPyth',
    version='1.0.1',
    author='Chui Tey',
    author_email='teyc@cognoware.com',
    packages=['Sablot', 'Sablot.test', ],
    package_data = {
        'Sablot.test': ['*.xsl', '*.xml'],
        },
    scripts=[],
    url='http://pypi.python.org/pypi/SabPyth/',
    license='LICENSE.txt',
    description='Interface to the Sablotron XSL processor',
    long_description=open('README.txt').read(),
    # these don't copy files to the libs
    #data_files = [
    #    ('Sablot/test', ['Sablot/test/sheet.xsl', 'Sablot/test/sheet4.xsl']),
    #    ],
    ext_modules = [
                   Extension('_sablot',
                             sources=['src/_sabpyth/Handlers.c',
                                      'src/_sabpyth/Processor.c',
                                      'src/_sabpyth/Sablotmodule.c',
                                      SABLOTRON_DIR + 'verts.cpp',
                                      SABLOTRON_DIR + 'arena.cpp',
                                      SABLOTRON_DIR + 'base.cpp',
                                      SABLOTRON_DIR + 'context.cpp',
                                      SABLOTRON_DIR + 'datastr.cpp',
                                      SABLOTRON_DIR + 'decimal.cpp',
                                      SABLOTRON_DIR + 'domprovider.cpp',
                                      SABLOTRON_DIR + 'encoding.cpp',
                                      SABLOTRON_DIR + 'error.cpp',
                                      SABLOTRON_DIR + 'expr.cpp',
                                      SABLOTRON_DIR + 'hash.cpp',
                                      SABLOTRON_DIR + 'jsdom.cpp',
                                      SABLOTRON_DIR + 'jsext.cpp',
                                      SABLOTRON_DIR + 'key.cpp',
                                      SABLOTRON_DIR + 'numbering.cpp',
                                      SABLOTRON_DIR + 'output.cpp',
                                      SABLOTRON_DIR + 'parser.cpp',
                                      SABLOTRON_DIR + 'platform.cpp',
                                      SABLOTRON_DIR + 'proc.cpp',
                                      SABLOTRON_DIR + 'sablot.cpp',
                                      SABLOTRON_DIR + 'sdom.cpp',
                                      SABLOTRON_DIR + 'situa.cpp',
                                      SABLOTRON_DIR + 'sxpath.cpp',
                                      SABLOTRON_DIR + 'tree.cpp',
                                      SABLOTRON_DIR + 'uri.cpp',
                                      SABLOTRON_DIR + 'utf8.cpp',
                                      SABLOTRON_DIR + 'vars.cpp',
                                      EXPAT_DIR + 'xmlparse.c',
                                      EXPAT_DIR + 'xmlrole.c',
                                      EXPAT_DIR + 'xmltok.c',
                                      EXPAT_DIR + 'xmltok_impl.c',
                                      EXPAT_DIR + 'xmltok_ns.c',
                                      ],
                             define_macros   = [
                                ('WIN32', None), 
                                ('__WIN_TOOLS', None), 
                                ('HAVE_MEMMOVE', None),],
                             include_dirs=[SABLOTRON_DIR, 'src/include'],
                             library_dirs=['lib', 'C:/python27/Libs',],
                             ), ]
)
