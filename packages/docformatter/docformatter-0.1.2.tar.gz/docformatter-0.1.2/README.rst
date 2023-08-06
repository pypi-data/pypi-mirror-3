============
docformatter
============

Formats docstrings to follow `PEP 257`_.

.. _`PEP 257`: http://www.python.org/dev/peps/pep-0257/

.. image:: https://secure.travis-ci.org/myint/docformatter.png
   :target: https://secure.travis-ci.org/myint/docformatter
   :alt: Build status

-------
Example
-------

After running::

    $ docformatter example.py

this::

    def launch_rocket():
        """Launch
    the
    rocket."""


    def factorial(x):
        '''

        Return x factorial.

        This uses math.factorial.

        '''
        import math
        math.factorial(x)


    def print_factorial(x):
        """Print x factorial"""
        print(factorial(x))


    def main():
        """Main
        function"""
        print_factorial(5)
        if factorial(10):
            launch_rocket()

gets formatted into this::

    def launch_rocket():
        """Launch the rocket."""


    def factorial(x):
        """Return x factorial.

        This uses math.factorial.

        """
        import math
        math.factorial(x)


    def print_factorial(x):
        """Print x factorial."""
        print(factorial(x))


    def main():
        """Main function."""
        print_factorial(5)
        if factorial(10):
            launch_rocket()

-------
Options
-------

Below is the help output::

    usage: docformatter [-h] [--in-place] [--no-backup] [--version]
                        files [files ...]

    Formats docstrings to follow PEP 257.

    positional arguments:
      files        files to format

    optional arguments:
      -h, --help   show this help message and exit
      --in-place   make changes to file instead of printing diff
      --no-backup  do not write backup files
      --version    show program's version number and exit
