`ikazuchi.plugins.pofile <https://bitbucket.org/t2y/ikazuchi.plugins.pofile>`_
is plugin for `ikazuchi <https://bitbucket.org/t2y/ikazuchi>`_ to transalte
PO file with good reference.

`ikazuchi` is intended to work with other tools since it's a CUI tool.

See the project `documentation <http://t2y.bitbucket.org/ikazuchi/build/html/index.html>`_ for more detail.

Features
========

* Translate GNU gettext catalog named PO file with good reference from web API

Setup
=====

by easy_install
----------------

Make environment::

   $ easy_install ikazuchi.plugins.pofile

by buildout
-----------

Make environment::

   $ hg clone https://bitbucket.org/t2y/ikazuchi.plugins.pofile
   $ cd ikazuchi.plugins.pofile
   $ python bootstrap.py -d
   $ bin/buildout


Usage
=====

Translate PO file with ikazuchi command::

    $ ikazuchi pofile examples/short_test.po 
    msgid:                   ikazuchi translation
    reference(Google):       [Actually, translated sentence]
    Input:

Show which plugins are available::

    $ ikazuchi -h
    usage: ikazuchi [-h] {rstfile,pofile,normal} ...

    positional arguments:
      {rstfile,pofile,normal}
                            available plugins. 'normal' means ikazuchi's standard
                            feature so it can be abbreviated

    optional arguments:
      -h, --help            show this help message and exit

Show pofile plugin help::

    $ ikazuchi pofile -h
    usage: ikazuchi pofile [-h] [-a API] [-e ENCODING] [-f LANG] [-q] [-t LANG]
                           [--version]
                           po_file

    positional arguments:
      po_file               target po file

    optional arguments:
      -h, --help            show this help message and exit
      -a API, --api API     APIs are ['google', 'microsoft']
      -e ENCODING, --encoding ENCODING
                            input/output encoding
      -f LANG, --from LANG  original language
      -q, --quiet           not to show original sentence to stdout
      -t LANG, --to LANG    target language to translate
      --version             show program's version number and exit


Requirements
============

* Python 2.6 or later
* ikazuchi 0.5.1 or later
* polib 0.5.5 or later
* setuptools or distriubte


License
=======

Apache License 2.0


History
=======

0.1.2 (2011-11-26)
------------------
* use Microsoft Translator as Default API

0.1.1 (2011-06-06)
------------------
* add subparser for pofile plug-in

0.1.0 (2011-06-03)
------------------
* first release

