trac2rst
========

I use ``trac2rst`` to help me in the task to pass documentacion
from trac to sphinx. I usally copy the trac wiki page to a temporaly file, run
the script, copy the output to the new rest file and do manual changes.

Features
--------

The idea is use the tool to do the more tedious work (I mean transforming
lists, links and inliners).
You *must* review and fix the result later.


It only processes:
 * Headers (sections at 4 levels)
 * Lists (bullets and numbered)
 * Trac links.
 * A subject of trac and rest inliners

It does **NOT support** (a lot):
 * Trac macros
 * Trac processors
 * Links between wiki pages
 * Rest definition lists, etc
 * Preformatting
 * Images
 * Tables
 * Footnotes
 * Anchors
 * Citations
 * Comments
 * A lot more ...

Usage example
-------------

Type trac2rst --help

You can view a simple wiki transfomation (used for manual test)::

  $ bin/trac2rst -i src/trac2rst/tests/wikitext.txt -u https://trac.yaco.es/project/  -o /tmp/test.rst && rst2html /tmp/test.rst /tmp/test.html && firefox /tmp/test.html


Disclaimer
----------
This is a *quick and dirty tool*. It does not use reST or wiki processor. The
work is done using regular expressions.

License
-------

``trac2rst``  is offered under the `MIT license
<http://www.opensource.org/licenses/mit-license.php>`_.

Authors
-------

``trac2rst`` is made available by `Yaco Sistemas
<http://www.yaco.es>`_


Credits
-------

- `Distribute`_
- `Buildout`_
- `modern-package-template`_
- `zest.releaser`_

.. _Buildout: http://www.buildout.org/
.. _Distribute: http://pypi.python.org/pypi/distribute
.. _`modern-package-template`: http://pypi.python.org/pypi/modern-package-template
.. _zest.releaser: http://pypi.python.org/pypi/zest.releaser
