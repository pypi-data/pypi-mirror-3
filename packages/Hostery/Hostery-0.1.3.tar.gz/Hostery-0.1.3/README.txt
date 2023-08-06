=======
Hostery
=======

A command line tool for pushing git snapshots to a web host. Hostery creates a browsable history for a project by uploading selected git commits to an FTP server.

Configure a Repository
======================

``$ hostery init``

Issue this command at the root level of a git repository. You will be prompted for  host information which is stored in a file called ``.hostery-config``, which will be automatically added to your ``.gitignore``.

If your server doesn't provide shell access, use the ``--ftp`` flag to connect via FTP instead. By default, hostery uses the ``rsync`` command to transfer files, which is markedly faster and can handle symlinks.

Usage
=====

``$ hostery mark``

1. Synchronizes with your remote git repository. Hostery will pause to allow you to resolve merge conflicts and the like.
2. Uploads the latest commit to your server at ``root/branch/commit_hash/``
3. Updates an index file at ``root/`` linking to all of your "marked" commits alongside an iframe.