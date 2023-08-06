Dovetail command line
=====================

Simple usage::

    > dovetail clean install

Dovetail will load build.py if present in the current directory and run the
clean and install Tasks.

Specify a different build file with -f (build files are standard Python files)::

    > dovetail -f ../mybuild.py install

Help
----

Print a complete list of command-line options::

    > dovetail -h

Print this usage::

    > dovetail --usage

Logging
-------

To control verbosity of the output:

    * -q keep Dovetail (mostly) quiet. Output from tasks will always be printed
    * -v more detail on the decisions Dovetail is taking.
    * -vv for detailed debugging of your build script.

Output from Tasks (from print, write or other IO command, sent to stdout and
stderr) will always be echoed, regardless of the verbosity.

Nesting: Dovetail can help you see the structure of the build using the -n
option. This indents more deeply nested tasks (and their stdout/stderr) so
you can quickly see Task dependencies::

    > dovetail -n install

Switch off nesting (if it is set in a configuration file) with -nn::

    > dovetail -nn install

Virtualenv
----------

Dovetail can optionally run the build in a virtual environment using
http://virtualenv.org with the -e option::

    > dovetail -e /path/to/virtual/environment install

By default, Dovetail will reuse an existing environment, or create a new one if
it is not present. To ensure a clean environment use the --clear option::

    > dovetail -e /path/to/virtual/environment --clear install

Note: If this option is used and virtualenv is not present on the path,
Dovetail will attempt to download and install virtualenv.

Reports
-------

Dovetail has several built-in reports that can be run after the build,
even if the build failed. Reports are specified by using the -r option (which
may be repeated for each report required), eg::

    > dovetail -r <report name> install
    > dovetail -r slow -r tasks install

Where <report name> is one of:

  slow
     Reports the slowest tasks in the run. The report lists the longest Tasks
     which together comprise 80% of the total run time. Tasks comprising
     the remaining 20%, or and those faster than 1ms are excluded

  tasks
     Prints the Tasks that ran in a hierarchical tree in text format

  modules
     Shows the portion of the Python package structure where build scripts
     have been loaded. This is helpful to understand how to reference Tasks
     by fully qualified name

  depend
     Shows the tree of build scripts loaded by other build scripts. This is
     helpful when reviewing automatic dependencies - Tasks which share the
     same name in dependent build scripts - and their ordering
