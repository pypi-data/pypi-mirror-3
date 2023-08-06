versions extension
******************

Display the version information for Mercurial and all installed extensions.

Installation
============

Use `pip` or `easy_install` to install the package::

    $ pip install hg-versions

Or install from the sources::

    $ tar xzf hg-versions-0.1.tar.gz
    $ cd hg-versions-0.1
    $ python setup.py install

Then add the extension to your Mercurial configuration (your .hgrc or mercurial.ini file)::

    [extensions]
    versions =

Usage
=====

By default only the Mercurial version and enabled extensions with version information are displayed::

    $ hg versions
    Mercurial version: 1.7.2

    enabled extensions:

     versions 0.1

You can use the `-a` argument to display all enabled extensions, even those without a version::

    $ hg versions -a
    Mercurial version: 1.7.2

    enabled extensions:

     bookmarks 
     color 
     crecord 
     extdiff 
     fetch 
     graphlog 
     hgattic 
     hggit 
     hgsubversion 
     histedit 
     mercurial_keyring 
     pager 
     prompt 
     rebase 
     versions 0.1
