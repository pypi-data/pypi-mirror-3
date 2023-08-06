setuptools_hg
=============

setuptools_hg is a plugin for setuptools/distribute to enable it to find
files under the Mercurial version control system.

It uses the Mercurial Python library by default and falls back to use the
command line programm `hg(1)`_. That's especially useful inside virtualenvs
that don't have access to the system wide installed Mercurial lib (e.g. when
created with ``--no-site-packages``).

.. note:: The setuptools feature

  You can read about the hooks used by setuptool_hg in the setuptools_ or
  distribute_ documentation. It basically returns a list of files that are
  under Mercurial version control when running the ``setup`` function, e.g. if
  you create a source and binary distribution. It's a simple yet effective way
  of not having to define package data (non-Python files) manually in MANIFEST
  templates (``MANIFEST.in``).

.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools#adding-support-for-other-revision-control-systems
.. _distribute: http://packages.python.org/distribute/setuptools.html#adding-support-for-other-revision-control-systems
.. _`hg(1)`: http://www.selenic.com/mercurial/hg.1.html

Usage
*****

Here's an example of a setup.py that uses setuptools_hg::

    from setuptools import setup, find_packages

    setup(
        name="HelloWorld",
        version="0.1",
        packages=find_packages(),
        setup_requires=["setuptools_hg"],
    )

If you run this setup.py setuptools will automatically download setuptools_hg
to the directory where the setup.py is located at (and won't install it
anywhere else) to get all package data files from the Mercurial repository.

Options
*******

Set the ``HG_SETUPTOOLS_FORCE_CMD`` environment variable before running
setup.py if you want to enforce the use of the hg command.
"""

CHANGES
*******

0.4
---

- fix a bug if the current distribution is not versionned with mercurial. [kiorky]
- fix https://bitbucket.org/jezdez/setuptools_hg/issue/5/using-hg-command-line-with-py3-does-not [kiorky]
