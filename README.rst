=================
AST library
=================

:Author: `Angus Griffith sn6uv`

At present this is essentially just a fork of pycparser by `Eli Bendersky`
with things moved round a little.

Introduction
============

Behaviour:
---------
Generating an AST framework::

    > python astlib/ast_gen.py some_ast.cfg

To see the full list of commands::

    > python astlib/ast_gen.py --help

You might just want to import the core stuff contained in astlib/ast_core.py and write an AST framework by hand.

