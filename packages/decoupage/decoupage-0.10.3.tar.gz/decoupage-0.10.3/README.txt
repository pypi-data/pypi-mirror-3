decoupage
=========

what is it?
-----------

decoupage is a static file server that allows for index pages
configurable with genshi templates and .ini files.  I mainly wrote it
because i was tired of using apache for serving my website and
generating index.html files by hand.  Decoupage provides views into
the filesystem.



how do i use it?
----------------

Set up a `paste <http://pythonpaste.org>`_ .ini file that specifies the
directory to serve (``decoupage.directory``) and, optionally, a
configuration file .ini file (``decoupage.configuraton``) which
specifies the labels for the files based on directory. An example of a
`paste <http://pythonpaste.org>`_ .ini file is in
``decoupage.ini``. Note the ``[app:decoupage]`` section::

    [app:decoupage]
    paste.app_factory = decoupage.factory:factory
    decoupage.directory = %(here)s/example
    decoupage.configuration = %(here)s/example.ini

The labels for files are in ``example.ini``, specified by sections as
directories::

    [/]
    foo.txt = a file about cats

    [/cats]
    lilly.txt = lilly
    hobbes.txt = a file about Hobbes

You can specify the entire layout from here.  Alternately, you can
have an ``index.ini`` in a directory which, if present, overrides the
default configuration.  Such a file is in the ``fleem`` subdirectory
of ``example``::

    /template = index.html
    fleem.txt = some fleem for ya

Try it out!  Install decoupage and run ``paster serve decoupage.ini``
and point your browser to the URL it gives you.


how do i do more with decoupage?
--------------------------------

Since filenames can't start with a ``/`` (just try it!), the
functionality of decoupage may be extended with ``/`` commands in a
section.  This is done by adding a setuptools ``entry_point`` to
``[decoupage.formatters]``.  See the decoupage ``setup.py`` and
``decoupage.formatters`` for examples.  For instance, 

Running `decoupage-formatters` from the command line gives the list of
formatters that are available (which are pluggable setuptools extension points
at [decoupage.formatters]).  For example: /include = site.html could
include the site.html genshi template at the top of the body.

Formatters:

sort: 
    determines how to sort the files in a directory; 
    right now only by case-insensitive alphabetically
    * reverse : reverse the order of the sorting
    
all: 
    only pass files of a certain pattern; 
    the inverse of ignore
    calling all with no arguments means only files with descriptions
    are used
    
title: 
    splits a description into a title and a description via a
    separator in 
    the description.  The template will now have an additional
    variable, 
    'title', per file
    Arguments:
    * separator: what separator to use (':' by default)
    
describe: 
    obtain the description from the filename
    the file extension (if any) will be dropped and
    spaces will be substituted for underscores
    
ignore: 
    ignore files of a glob patterns.  
    These files will not be linked to in the template.
    e.g. /ignore = .* *.pdf  # don't list dotfiles and PDFs
    
include: include a file at the top of the body
css: specify CSS used (whitespace separated list)

Decoupage also makes use of other special intrinsic keywords:

formatters: ordered list of formatters to apply

inherit: inherit configuration from a certain directory (instead of
the parent

transform: a list of transformers for contenttransformer


TODO
----

 * allow transformers to be configurable on a per-directory basis
 * add a ``?format=rss`` query string argument
 * add a ``?template=foo.html`` query string argument
