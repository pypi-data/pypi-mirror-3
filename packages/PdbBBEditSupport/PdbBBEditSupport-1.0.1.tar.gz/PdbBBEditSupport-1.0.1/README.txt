PdbBBEditSupport 1.0
=======================

View your source code in BBEdit while debugging with pdb
----------------------------------------------------------

This module is used to hook up pdb_, the python debugger, with BBEdit_, a
text editor for Mac OS X, enabling it to display the
debugged source code during a pdb_ session.

.. _pdb: http://docs.python.org/lib/module-pdb.html
.. _BBEdit: http://barebones.com/

After downloading and unpacking the package, you should install the helper
module using::

  $ python setup.py install

Next you need to hook up pdb_ with this module by add the following to your
``.pdbrc``::

  from PdbBBEditSupport import preloop, precmd
  pdb.Pdb.preloop = preloop
  pdb.Pdb.precmd = precmd

The easiest way to do this is to use the provided script::

  $ pdbbbsupport enable

Alternatively you can also do it manually.  The ``.pdbrc`` is located in your
home folder and possibly needs to be created first.  You may also use the
supplied sample configuration file for pdb_ to enable the hook like::

  $ cp pdbrc.sample ~/.pdbrc

Afterwards BBEdit_ should get started automatically whenever you enter a
debug session.  The current source line will be displayed simultaneously while
stepping through the code.  However, having the cursor moved automatically
within that source file is not always very obvious, so you might want to use
the "Highlight insertion point: Line color" feature, which can be enabled in the "Text Colors"
tab in BBEdit's preferences.

Updated for BBEdit by Matthew Schinckel <matt@schinckel.net>

Original author of TextMate version:

Andreas Zeidler, az@zitc.de,
2007/02/18
