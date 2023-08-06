========
 Shrink
========

Shrink is a command for concatenating and compressing css stylesheets and
javascript files making them smaller.
Shrinking (or minifying) these files reduces the number of request that are
made after a page load and also the size of these requests.

This command depends on `YUI Compressor <http://developer.yahoo.com/yui/compressor/>`_
to do the work, and can be run with Python 2.5 and above.

INI style config files are used to know which files will be minified and
also to know which ones will be merged before minimization.

To display script information and options run::

  $ shrink -h


Minimize css and js files
=========================

To minimize all files, run::

  $ shrink -f example_shrink.cfg all

This will use ``yuicompressor.jar`` and the ``example_shrink.cfg`` file in
current directory to compress all files.

In case that minimzation is not desired for all files, is also possible to
minimize individual files, or a group of files, by using the name(s) of each
section instead of ``all`` as argument.

To list available sections, run::

  $ shrink -f example_shrink.cfg -l


Config file format
==================

Config file is an INI file with a section defined for each individual file that
can be generated.

For minification of a single file a section would be written as::

  [sample-single-file-js]
  source_directory = %(base_dir)s/js
  destination_file = sample-file.min.js
  source_files = sample-file.js

Section options:
  * ``source_directory`` value will point to the directory where file(s)
    listed in ``source_files`` are located.
  * ``source_files`` value can be a single file name, or a list of file names.
    When a list of names is given, each file in list is concatenated (from top
    to down) into a single file before compression.
  * ``destination_directory`` When this value is present it is used as output
    directory for the minified file. By default minified file is generated in
    source directory.
  * ``destination_file`` value is the name for the minified file.
  * ``hash`` when true include destination file in shrink hash.
    See `Shrink hash file`_.


Many files can be specified to be concatenated into a single file that will be
named with the value given in ``destination_file``, by writing a section like::

  [sample-multiple-file-css]
  source_directory = %(base_dir)s/css
  destination_file = sample-multiple-file.min.css
  source_files =
      sample-file1.css
      sample-file2.css
      sample-file3.css

Section groups
--------------

Instead of running script with ``sample-single-file-js`` and
``sample-multiple-file-css`` as arguments is possible to define a group like::

  [sample-group]
  group =
      sample-single-file-js
      sample-multiple-file-css

And then run minifier script with ``sample-group`` as parameter.

Shrink hash file
----------------

After minification Shrink can create a file containing a SHA1 hash. The file
is created when at least one section in config file has ``hash = true``. Hash
is created using the contents of all destination files in these sections.

This is useful to know when some files changed, and to reload static css and
javascript files without using a timestamp or version number.
Sometime can be desirable to reload modified static files without increasing
application version. In these cases the hash can be used as request parameter
instead of version number.
