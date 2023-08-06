#!/usr/bin/env python

from distutils.core import setup, Command

#XXX waw. still cannot follow symlinks. such a dinosaur..
#from tarfile import TarFile
#TarFile.dereference = True

Command.cp=Command.copy_file
def copy_file(self,
                    infile, outfile,
                    preserve_mode=1, preserve_times=1, link=None, level=1):
    return Command.cp( self,
                    infile, outfile,
                    preserve_mode=preserve_mode, preserve_times=preserve_times, link=None, level=level)
Command.copy_file = copy_file


setup(
    name= 'sklad',
    version= '0.1',
    description= 'tiny wsgi file-uploader - multiple or single selections, progress-per-file, unlimited size',
    author= 'svilen dobrev',
    author_email= 'az@svilendobrev.com',
    scripts= '''
            sklad.wsgi
            jquery.fileupload.js
            jquery.fileupload.auto.js
            jquery.js
            fileupload.css
            25/cgi.py
            '''.split(),
    license = "MIT License",

    classifiers='''
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Environment :: Web Environment
Topic :: Internet :: WWW/HTTP :: WSGI
Topic :: Software Development :: Libraries :: Python Modules
'''.strip().split('\n'),

    long_description= '''\
a tiny cut from gp.fileupload-1.1, doing the actual job, with fixes and extensions.
 * as HTML form, or jquery with multiple progress-per-upload;
 * as single file and multiple file selections (HTML5)
 * ok with UTF8 or cp1251 encoded non-ascii filenames
 * ok with any file-sizes - doesn't store anything in memory
 * uses os.path.getsize() to measure actual progress. hacks cgi.FieldStorage to handle tiny files (<1000 bytes)

usage:
 * in sklad.wsgi, application(), change the head/tail for needed html (default is both form and jquery).
 * change FieldStorage.PATH to where files should be stored (relative)
 * the relevant client file is jquery.fileupload.js, to change progress-representation.
 * tweak .htaccess or in other way make sklad.wsgi accessible to apache (AddHandler wsgi-script .wsgi)
 * for logging, uncomment fdebug and may change tpath
 * hack it all as u like

notes for python version 2.5 and below:
 * standard-lib cgi.py does not work - use the hacked/backported 25/cgi.py (put in same dir or fix imports in sklad.wsgi)
 * there's no json module in standard-lib; install simple_json instead

have fun
www.svilendobrev.com
'''

)

# vim:ts=4:sw=4:expandtab
