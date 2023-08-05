======================================
 ikazuchi - simple translation helper
======================================

`ikazuchi <https://bitbucket.org/t2y/ikazuchi>`_
helps to translate document using web translate APIs efficiently.
`ikazuchi` is intended to work with other tools since it's a CUI tool.

********
Features
********

Now, `ikazuchi` is under development.

* `ikazuchi` can use 2 APIs,
  `Google Translate API <http://code.google.com/intl/ja/apis/language/translate/overview.html>`_,
  `Microsoft Translator <http://www.microsofttranslator.com/dev/>`_.
  (`Yahoo! Pipes <http://pipes.yahoo.com/pipes/>`_ is not supported as formal feature.)
* Translate GNU gettext catalog named PO file with good reference from web API
* Translate reST document file keeping with the format
* Translate any string passed from command line argument
* Translate any string in Vim using ":pyfile" command
* Detect language of any string passed from command line argument

.. seealso::

   See :ref:`terms_of_use` for each APIs you want to use.

===================
 Command Reference
===================

Usage
-----

All command option are::

    $ ikazuchi -h
    usage: ikazuchi [-h] [-v] [-a API] [-d] [-e ENCODING] [-f LANG] [-l]
                    [-p POFILE] [-q] [-r RSTFILE] [-s SENTENCE [SENTENCE ...]]
                    [-t LANG]

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -a API, --api API     APIs are ['google', 'microsoft']
      -d, --detect          detect language for target sentence
      -e ENCODING, --encoding ENCODING
                            input/output encoding
      -f LANG, --from LANG  original language
      -l, --languages       show supported languages
      -p POFILE, --pofile POFILE
                            target po file
      -q, --quiet           not to show original sentence to stdout
      -r RSTFILE, --rstfile RSTFILE
                            target reST file
      -s SENTENCE [SENTENCE ...], --sentences SENTENCE [SENTENCE ...]
                            target sentences
      -t LANG, --to LANG    target language to translate

Indent paragraph
----------------

    Given multi sentences
    are translated
    on the fly. 

Line block
----------

| If "sentence:" line is not needed, **-q** option cuts off it.
|   It can change the translate API with **-a** option.
|     It can change the source and destination languages with **-f** and **-t**
|     option.  For example, it translates Japanese text to German.

Hyper link
----------

`ikazuchi`_ 's source is hosted on bitbucket.

.. _ikazuchi: <https://bitbucket.org/t2y/ikazuchi>

Lists
-----

1. Translate with Commnad line
2. Translate with PO file

  * show good reference
  * use reference string

#. Translate with RST file
#. Translate with VIM

  - `raimei` is used for paragraph
  - `enrai` is used for word

Tables
------

+----------+-------+-----------------------------+
| name     | parse | description                 |
+==========+=======+=============================+
| ikazuchi | noun  | it means thunder            |
+----------+-------+-----------------------------+
| izuchi   | noun  | it means flash of lightning |
+----------+-------+-----------------------------+

======  =========  ===============
name    use        description
======  =========  ===============
raimei  paragraph  bronto
enrai   word       faraway thunder
======  =========  ===============

Directive
---------

.. seealso::

    Module :mod:`ikazuchi`
        `ikazuchi <https://bitbucket.org/t2y/ikazuchi>`_
        helps to translate document using web translate APIs efficiently.
        `ikazuchi` is intended to work with other tools since it's a CUI tool.

    :ref:`ikazuchi document`
        Documentation of ikazuchi.
