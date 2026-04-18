|Workflows| |Pypi Installs| |Latest Version| |Supported Python Versions|

|Packaging status|

Mathics3 Character Tables and Scanner
=====================================

This repository really contains two things:

* extensive tables describing WL symbols, operators, and their properties
* a tokenizer or scanner portion for the Wolfram Language.

Concerning the first item, there are two commented YAML files that contain a
full set of translations between:

* Wolfram Language named characters,
* Unicode/ASCII equivalents and Unicode and WL code-points,
* AMSLaTeX equivalent names,
* Operator name (if symbol is an operator),
* Operator arity (if an operator)
* Operator precedence (if an operator)
* Operator associativity (if an operator)
* Keyboard escape sequences for the symbol

Uses
----

The scanner and character tables are used inside `Mathics3 <https://mathics.org>`_. However information can
also be used by other programs for tokenizing and formatting Wolfram Language code.

For example, tables are used in `mathics-pygments <https://pypi.org/project/Mathics-Scanner/>`_, a Pygments-based
lexer and highlighter for Mathematica/Wolfram Language source code.

This library may be useful if you need to work with the Wolfram Language
named character and convert it to various formats.

Usage
-----

- For tokenizing and scanning Wolfram Language code, use the
  ``mathics_scanner.tokenizer.Tokenizer`` class.
- To convert between Wolfram Language named characters and Unicode/ASCII, use
  the ``mathics_scanner.characters.replace_wl_with_plain_text`` and
  ``mathics_scanner.characters.replace_unicode_with_wl`` functions.
- To convert between qualified names of named characters (such ``FormalA`` for
  ``\[FormalA]``) and Wolfram's internal representation use the
  ``m̀athics_scanner.characters.named_characters`` dictionary.

To regenerate JSON-format tables, run:

::

   $ bash admin-tools/make-JSON-tables.sh

Utility for showing token parsing
---------------------------------

There is a command-line utility, ``mathics3-codeparser-tokenize``, for showing how
an input stream is tokenized. The ``--CodeTokenize`` or ``-C`` option
will try to show the token similar to how it would appear using the ``CodeParser`CodeTokenize``. Type
``mathics3-codeparser-tokenize --help`` information on command-line options.

Implementation
--------------

For notes on the implementation of the packages or details on the conversion
scheme, please read `Mathics3 scanner's documentation <https://mathics3-scanner-and-yaml-tables-for-characters-and-operators.readthedocs.io/en/latest/>`_ or
`Scanning section <https://mathics-development-guide.readthedocs.io/en/latest/code-overview/scanning.html>`_ of the Mathics3 User and Developers Guide.

Contributing
------------

Please feel encouraged to contribute to this package or Mathics3! Create your
own fork, make the desired changes, commit, and make a pull request.

License
-------

Mathics3 is released under the GNU General Public License Version 3 (GPL3).

.. |Workflows| image:: https://github.com/Mathics3/mathics-scanner/actions/workflows/ubuntu.yml/badge.svg
.. |Packaging status| image:: https://repology.org/badge/vertical-allrepos/mathics-scanner.svg
			    :target: https://repology.org/project/mathics-scanner/versions
.. |Latest Version| image:: https://badge.fury.io/py/Mathics-Scanner.svg
		 :target: https://badge.fury.io/py/Mathics-Scanner
.. |Pypi Installs| image:: https://pepy.tech/badge/Mathics-Scanner
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/Mathics-Scanner.svg
