==========================
tl.buildout_virtual_python
==========================

This is a `zc.buildout` recipe for setting up a virtual Python installation
inside a buildout. It is compatible with Python versions 2.5 through 2.7 and
`zc.buildout` versions 1.4 and upwards.

The implementation makes use of the `virtualenv` package, originally by Ian
Bicking.

This recipe appears to be reliable, but the feature set is basically
determined by the author's immediate needs. Don't hesitate to send questions,
bug reports, suggestions, or patches to <thomas@thomas-lotze.de>.


Use cases
=========

Using a virtual Python gives you a Python environment which is writable for
other parts of the buildout without the need to compile Python from source. It
is isolated from other buildouts as well as from its parent Python
installation while it may still share the parent Python's installed libraries.
Depending on your situation, these features may be considered helpful or
harmful. The recipe provides mechanism and leaves choosing policy up to you.

Another aspect is that of providing a real Python executable which has access
to libraries installed by the buildout. Normally, `zc.buildout` makes
installed Python libraries accessible by creating the Python scripts in
``bin/`` as wrappers that set up an appropriate ``sys.path`` and then call one
of the ``console_script`` entry points of some installed egg. Sometimes this
isn't a workable approach, for example:

  * when one of the programs calls ``sys.executable`` and expects it to have
    the same libraries installed that the calling code can import

  * when the code being installed is intended to be run by an embedded Python
    interpreter, such as when setting up a `mod_python` application

In those cases, install the required libraries into a virtual Python
environment and use that as another buildout part's Python installation.


Options
=======

A buildout part created by this recipe exports an ``executable`` option so it
may be used as a part defining a Python installation in a buildout, i.e. a
buildout section's ``python`` option may reference it.

Configuration options:
    :executable-name:
        Basename of the virtual Python installation's interpreter executable.

    :interpreter:
        Basename of a Python interpreter in the buildout's ``bin`` directory
        that uses the virtual Python installation. No such interpreter is
        created if the option is not set.

    :real-python:
        Filesystem path to the interpreter executable of the Python
        installation that should be used as the parent Python.

    :site-packages:
        Boolean switch, whether to make the parent Python's ``site-packages``
        library directory available to the virtual Python.

    :eggs:
        Specifications of eggs to be available to the virtual Python.

    :extra-paths:
        Extra library paths to make available to the virtual Python.

Exported options:
    :location:
        Location of the buildout part containing the virtual Python
        installation. This is the same as the virtual Python's ``sys.prefix``.

    :executable:
        Filesystem path to the interpreter executable of the virtual Python
        installation.


.. Local Variables:
.. mode: rst
.. End:
