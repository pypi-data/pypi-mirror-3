====
Pyng
====

Pyng is a collection of Python utility functions I've written over the years,
and that I keep wishing were available everywhere. Sadly, in many cases I've
simply pasted copies of individual functions as needed. But no more!

It's organized as follows:

* **exc:** manipulate exceptions, e.g. reraise, retry

* **iters:** generic iterator functionality, akin to itertools

* **genio:** generator-based file I/O, loosely related to Java file streams

* **relwalk:** os.walk() filtered to produce pathnames relative to the
  starting directory

* **replacefile:** filter a text file in-place

Please see the individual docstrings for more information.
