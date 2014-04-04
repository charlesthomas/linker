======
linker
======
.. image:: https://travis-ci.org/charlesthomas/linker.svg?branch=python3
        :target: https://travis-ci.org/charlesthomas/linker

``linker`` is a tool for symlinking files based on the name of original file.

Python Support
--------------
``linker`` is supported under python 2.6, 2.7, 3.3, and 3.4

Why use ``linker``?
-------------------
``linker`` takes a target directory and a destination directory as arguments,
and links everything from the repo into its correct location, determined by the
name of the target file. This allows you to track files in git, edit them in
the place you would normally find them, and deploy your config quickly to new
machines by cloning. Files common to all machines can be linked at the same time
as config files unique to a specific host; all in the same repo.

See `Example`_ for further detail.

Usage
-----

::

    Usage: linker.py [options] target destination

    Options:
      -h, --help            show this help message and exit
      -i, --interactive     Prompt for all changes
      -v, --verbose         Print all changes
      -d, --dry-run         Print all changes, but DON'T DO THEM
      -x, --exclude-common  default is to link files in `hostname` and 'common'
                            dirs. this will only link `hostname`
      --delete-existing     delete existing files instead of moving them to
                            original_name.back
      -m, --move-first      move a file from its original location to the repo
                            first, then link it back to its original location
      -c, --common-target   only used with --move-to-target-first, this will move
                            the original file to common, instead of hostname
                            before linking back to its original location

Deterministic File Names
------------------------
``linker`` makes a few assumptions:

- The git repo (or whatever else the target path happens to be) will have at
  least one folder in it, which matches the hostname of the machine ``linker``
  is running on. This allows multiple machine configs to be kept in the same
  repo.

- If a target file ends with ".dontlink" it should be tracked in the repo, but
  not linked by ``linker``.

- Underscores (_) in the target file should be replaced with slashes (/) in the
  symlink. This allows you to keep all the files for a single host in the same
  directory level of the repo, but be multiple levels deep where the link is
  made.

- A double underscore in the target file is a literal underscore in the link
  name.

- A file that starts with an underscore should be linked from ``/``, not from
  the destination root.

- If a directory named "common" exists at the same level as the hostname
  directory, those files should be linked, too. (This allows some files to link
  on all machines in the repo.)

- If a file already exists, it should be backed up (moved to
  original_name.back), unless you explicity include ``--delete-existing``.

Vanilla Example
---------------
The user "user" keeps their dot files in a repo called "dotfiles" and
they want to use ``linker`` on a machine called "hostname".

::

    - /home/user/git/dotfiles
        - hostname
            - .vimrc
            - .vim_colors_color__scheme.vim
            - crontab_backup.dontlink
            - _etc_hosts
        - common
            - .bashrc

With the command::

    linker /home/user/git/dotfiles /home/user

``linker`` would make the following symlinks::

    - /home/user/.bashrc -> /home/user/git/dotfiles/common/.bashrc
    - /home/user/.vimrc -> /home/user/git/dotfiles/hostname/.vimrc
    - /home/user/vim/colors/color_scheme.vim -> /home/user/git/dotfiles/hostname/.vim_colors_color__scheme.vim
    - /etc/hosts -> /home/user/git/dotfiles/hostname/_etc_hosts

Notice crontab_backup.dontlink wasn't linked anywhere.

Move First Example
------------------
If you already have your files named appropriately, using ``linker`` is easy. If
you don't, the naming scheme can be confusing. Using ``linker -m [-c]`` will
*hopefully* make this easier.

"User" has a repo "dotfiles" on a machine called "hostname" and wants to add
``/etc/hosts`` to the dotfiles repo::

    linker -m /home/user/git/dotfiles /etc/hosts

``linker`` will **move** ``/etc/hosts`` to
``/home/user/git/dotfiles/hostname/_etc_hosts`` and then link that file back to
``/etc/hosts``::

    - /etc/hosts -> /home/user/git/dotfiles/hostname/_etc_hosts

Doing the same, but adding the ``-c`` option::

    linker -m -c /home/user/git/dotfiles /etc/hosts

``linker`` will move ``/etc/hosts`` to
``/home/user/git/dotfiles/common/_etc_hosts`` instead of
``../hostname/_etc_hosts``::

    - /etc/hosts -> /home/user/git/dotfiles/common/_etc_hosts

This option was intended to be used **one file at a time**, and ``destination``
must be the full file path.

To Do
-----
See `todo.md`_

.. _Example: https://github.com/charlesthomas/linker#vanilla-example
.. _todo.md: https://github.com/charlesthomas/linker/blob/master/todo.md
