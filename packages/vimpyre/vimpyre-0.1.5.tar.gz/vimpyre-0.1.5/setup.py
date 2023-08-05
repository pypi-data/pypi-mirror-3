from setuptools import setup, find_packages

version = '0.1.5'

setup(name='vimpyre',
      version=version,
      description="Vim Scripts Manager (use pathogen, git, and python!)",
      long_description="""\
Vimpyre
=======

Vimpyre, Vim Scripts Manager (use pathogen, git, and python!)

Actions:
    init, syncdb, install, search, remove, update, browse, remove_all, update_all, list_installed, list_all

Requirements
------------

1. git
2. python
3. python-plac (http://pypi.python.org/pypi/plac)
4. python-simplejson (http://pypi.python.org/pypi/simplejson)

Install
-------
Step::

    $ git clone git://github.com/pct/vimpyre.git
    $ cd vimpyre; sudo python setup.py install

Usage
-----
- Init (get pathogen.vim and create ~/.vim/vimpyre)::

    $ vimpyre init
    ( Please add 'call pathogen#runtime_append_all_bundles("vimpyre")' to your .vimrc manually.)

- SyncDB (get github vim-scripts repository)::

    $ vimpyre syncdb

- Search (Search vim-scripts from local repository)::

    $ vimpyre search html5.vim

- Install (git clone vim-scripts to ~/.vim/vimpyre)::

    $ vimpyre install html5.vim rails.vim calendar.vim

- List Installed (list ~/.vim/vimpyre directories)::

    $ vimpyre list_installed

- List All Scripts (list ~/.vim/vimpyre.json)::

    $ vimpyre list_all

- Update (git pull)::

    $ vimpyre update html5.vim rails.vim

- Update All (git pull all repositories)::

    $ vimpyre update_all

- Remove (rm ~/.vim/vimpyre/<vim-scripts>)::

    $ vimpyre remove rails.vim html5.vim

- Remove All (rm ~/.vim/vimpyre*)::

    $ vimpyre remove_all
    (If you want to use vimpyre again, please `vimpyre init; vimpyre syncdb` first!)

- Browse (open script's homepage on vim.org)::

    $ vimpyre browse calendar.vim

Todo
----

- HomeBrew like command

- Search/Install scripts from github [VimL]

- Install from any git repos what user given.

Change Log
-----------

- Version 0.1.5

  * NEW: add `vimpyre browse <script_name>` to browse vim scripts page
  * CHANGE: vimpyre code refactoring

""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='vim scripts manager',
      author='Daniel Lin',
      author_email='linpct@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'plac>=0.7.4',
          'simplejson>=2'
          # -*- Extra requirements: -*-
      ],
      entry_points={
      'console_scripts': [
          'vimpyre = vimpyre.vimpyre:main',
          ],
      },
      )
