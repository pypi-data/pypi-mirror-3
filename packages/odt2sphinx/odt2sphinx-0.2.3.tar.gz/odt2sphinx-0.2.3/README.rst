odt2sphinx
==========

What is it ?
------------

Odt2sphinx converts OpenDocument Text file(s) to one or several .rst files.

Install
-------

You need to install PIL first, then::

    pip install odt2sphinx

or

::
    
    easy_install odt2sphinx

Usage
-----

::

    Usage: 
      odt2sphinx [options] filename.odt [targetdir]
      odt2sphinx [options] config.cfg

    config.cfg content:
      [path/to/the/file.odt]
      targetdir = path/to/the/targetdir

    Options:
      -h, --help            show this help message and exit
      --debug               
      --download-source-link

Ouput files
-----------

The files are generated in the target dir, which by default has the 
same name as the .odt file minus the extension.

At least one file, "index.rst", will be written. Depending on the
document content, additional rst files may be generated (see next chapter).

Images are extracted and put together in an "images" directory inside
the targetdir.

Styles mapping
--------------

The following rules will be applied to particulary styles when converting
an .odt file. The style names are case-insensitive.

-   "Title" (in any language) : becomes the main document title
    (underlined with '=').

-   "Title 1" : Creates a new page named after the title, and becomes this
    page main title (underlined with '='). A reference to this file
    is inserted in a ``.. toctree`` directive of the index.rst file.

-   "Title 2" to "Title 6" : becomes sub-chapter titles.
    (underlined respectively '-', '~', '^', '"', "'")

-   "Warning" (or "Avertissement") : The chapter becomes the content
    of a ``.. warning`` directive

-   "Tip" (or "Trucs & Astuces") : The chapter becomes the content
    of a ``.. tip`` directive

-   "Note" or "Information": The chapter becomes the content
    of a ``.. note`` directive

Changes
-------

0.2.3 (2012-09-06)
~~~~~~~~~~~~~~~~~~

-   Fix filename generation by replacing any non-alphanumeric character
    (issue #3).

-   Fix handling of non-styled lists.

0.2.2 (2012-07-04)
~~~~~~~~~~~~~~~~~~

-   Fix the sdist archive on pypi.

0.2.1 (2012-06-24)
~~~~~~~~~~~~~~~~~~

-   Add support for numbered lists, hyperlinks, underlined text (translated to
    italic).

-   Fix bold text support.

0.2 (2012-05-28)
~~~~~~~~~~~~~~~~

-   Now supports python 3

-   Explicitely added PIL as a dependency (issue #2).

0.1.2 (2012-05-22)
~~~~~~~~~~~~~~~~~~

-   Add "Information" to the styles mapping.

-   Handle note, tip and warning styles in lists items. This allows to use
    lists inside a note, a tip or a warning.

-   Now handle external images (issue #1).

0.1.1 (2011-12-20)
~~~~~~~~~~~~~~~~~~

-   Improved the RstFile for use in third-party code: it is now possible
    to insert code and not just append it.

-   Add a README file

0.1.0
~~~~~

Initial release
