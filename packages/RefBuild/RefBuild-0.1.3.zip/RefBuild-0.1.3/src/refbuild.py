# -*- coding: utf-8 -*-
"""
Builds the preliminary reStructuredText files necessary for the 
documentation of Python source files from docstrings in the code.
    
This works with Sphinx and requires its "autodoc" option.

Installation
------------

Install with pip or easy_install such as::
    
    pip install refbuild
    
You may need to be root to have privileges.
    
Preliminaries
-------------

Run ``sphinx-quickstart`` on the command line to create a
Sphinx ``conf.py`` file. Be sure to select that you want autodoc on.
After you create the ``conf.py`` file, add a line so that it points to the
source files.
    
This package is arranged as::
    
    /doc
        /source
            conf.py
            index.rst
    /src
        refbuild.py
    
So ``conf.py`` needs the line::
    
    sys.path.insert(0, os.path.abspath('relative/path/to/src'))

Which in the tree structure presented here is::
    
    sys.path.insert(0, os.path.abspath('../../src'))
    
so that it can find the source file. This line should follow the import
statements of ``conf.py``.

Usage
-----
    
Run ``buildref`` from a command line in the directory where your source 
files are located::
    
    $ buildref
    
You will be asked a few questions and this will make a ``refconf.py`` 
file alongside your existing sources. You can easily edit this file
later in case you want to exclude some sources or change titles.

reStructuredText files are created where you specified (probably in
the same location as the ``conf.py`` and ``index.rst`` files). 
Make sure the ``index.rst`` file contains a reference
to ``api`` either as::
    
    .. include:: api.rst

or added to the table of contents as in::
    
    .. toctree::
    
        api

Assuming that a Sphinx makefile exists then executing ``make html`` 
or ``make latex`` should compile the documentation.

AUTHORS:

- THOMAS MCTAVISH (2011-12-01): initial version. Borrows heavily from
    sphinx-quickstart, version 1.0.7.
"""
__version__ = 0.1
import os, sys
from os import path
from sphinx.util.console import purple, bold, red, turquoise, \
    nocolor, color_terminal

PROMPT_PREFIX = '> '

def build():
    """
        Build the  files.
    """
    global modules, outpath, title, header
            
    # Write the api.rst file
    filepath = os.path.join(os.getcwd(), outpath, 'api.rst')
    with open(filepath, 'w') as api_file:
        api_file.write('.. _api:\n\n')
        for i in title:
            api_file.write('#')
        api_file.write('\n')
        api_file.write(title)
        api_file.write('\n')
        for i in title:
            api_file.write('#')
        api_file.write('\n')
        api_file.write('.. index::\n')
        api_file.write('   single: %s\n\n' %(title))
        api_file.write(header)
        api_file.write('\n\n.. toctree::\n\n')
        for modulename in modules:
            api_file.write('   ' + modulename + '\n')
        
    # Write the other files to include in the API.
    for modulename in modules:
        try:
            filepath = os.path.join(os.getcwd(), outpath, modulename + '.rst')
            fout=open(filepath, 'w')
            fout.write(modulename+'\n')
            for i in range(len(modulename)):
                fout.write('-')
            fout.write('\n\n')
            fout.write('.. This file has been automatically generated ')
            fout.write('by the refbuild module\n\n')
            fout.write('.. automodule :: %s\n' % (modulename))
            fout.write('   :members:\n\n')
        except:
            print "could not generate doc for {0}".format(modulename)
            fout.close()
            pass
        fout.close()

def mkdir_p(dir):
    if path.isdir(dir):
        return
    os.makedirs(dir)

class ValidationError(Exception):
    """Raised for validation errors."""

def is_path(x):
    if path.exists(x) and not path.isdir(x):
        raise ValidationError("Please enter a valid path name.")
    return x

def nonempty(x):
    if not x:
        raise ValidationError("Please enter some text.")
    return x

def boolean(x):
    if x.upper() not in ('Y', 'YES', 'N', 'NO'):
        raise ValidationError("Please enter either 'y' or 'n'.")
    return x.upper() in ('Y', 'YES')

def do_prompt(d, key, text, default=None, validator=nonempty):
    while True:
        if default:
            prompt = purple(PROMPT_PREFIX + '%s [%s]: ' % (text, default))
        else:
            prompt = purple(PROMPT_PREFIX + text + ': ')
        x = raw_input(prompt)
        if default and not x:
            x = default
        if x.decode('ascii', 'replace').encode('ascii', 'replace') != x:
            if TERM_ENCODING:
                x = x.decode(TERM_ENCODING)
            else:
                print turquoise('* Note: non-ASCII characters entered '
                                'and terminal encoding unknown -- assuming '
                                'UTF-8 or Latin-1.')
                try:
                    x = x.decode('utf-8')
                except UnicodeDecodeError:
                    x = x.decode('latin1')
        try:
            x = validator(x)
        except ValidationError, err:
            print red('* ' + str(err))
            continue
        break
    d[key] = x

def build_conffile(d):
    temp = {}
    print '''
    A "refconf.py" file will be created alongside existing sources.
    With this file, you can edit the modules that are translated 
    and modify other parameters specified in the file.'''

    print '''
    Enter the output directory for the '.rst' files.
    This should be the same location where the Sphinx 'conf.py'
    file is located.'''
    do_prompt(d, 'outpath', 'Relative path for the documentation', '.', is_path)
    
    if path.isfile(path.join(d['outpath'], 'conf.py')) is False and \
        path.isfile(path.join(d['outpath'], 'source', 'conf.py')) is False:
            print
            print bold('Warning: an existing Sphinx "conf.py" file has '
                       'not been found in this path.')
            do_prompt(temp, 'continue', 'Continue? (Y/n)', 'y', boolean)
            if not temp['continue']:
                sys.exit(1)
    else:
        print bold('IMPORTANT: Be sure that the Sphinx "conf.py" contains the line:')
        print bold('sys.path.append(os.path.abspath(\'path/to/source\'))')

    if not path.isdir(d['outpath']):
        mkdir_p(d['outpath'])
    
    do_prompt(d, 'title', 'Title', 'Source Reference')
    do_prompt(temp, 'name', 'Specify the project name')

    d['header'] = 'This is the source reference for the %s project.' %(temp['name'])

    # Files to include in the API.
    d['modules'] = []
    dirlist = os.listdir(os.getcwd())
    for item in dirlist:
        if item.endswith('.py') and \
                item.startswith('_') is False and \
                item != 'refconf.py':
            d['modules'].append(item[:-3])

    with open('refconf.py', 'w') as conffile:
        conffile.write('# -*- coding: utf-8 -*-\n')
        conffile.write('"""\n')
        conffile.write('This file has been generated by the RefBuild %s utility.\n\n' %__version__)
        conffile.write('You can either regenerate this file by running::\n\n')
        conffile.write('    $ buildref\n\n')
        conffile.write('or edit items such as the list of modules that are included for processing.\n"""\n\n')
        for (k,v) in d.iteritems():
            conffile.write(k)
            conffile.write(' = ')
            conffile.write(repr(v))
            conffile.write('\n')

    do_prompt(temp, 'continue', '"refconf.py" file has been created.\nContinue to build ".rst" files? (y/N)', 'y', boolean)

    return temp['continue']

def inner_main(args):
    d = {}
    temp = {}
    
    if not color_terminal():
        nocolor()

    print bold('Welcome to the RefBuild %s utility.') % __version__
    print '''
    Please enter values for the following settings (just press Enter to
    accept a default value, if one is given in brackets).
    '''

    temp['buildconf'] = not path.isfile('refconf.py')
    if not temp['buildconf']:
        do_prompt(temp, 'buildconf', '"refconf.py" file already exists. Rebuild it? (y/N)', 'n', boolean)
    
    proceed = True
    if temp['buildconf']:
        proceed = build_conffile(d)
    
    if proceed:
        try:
            execfile('refconf.py', globals()) # load global vars
        except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
            if errno == 2:
                print "Cannot find the file \'{0}\'".format(python_file)
            raise
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        build()


def main(argv=sys.argv):
    try:
        return inner_main(argv)
    except (KeyboardInterrupt, EOFError):
        print
        print '[Interrupted.]'
        return


