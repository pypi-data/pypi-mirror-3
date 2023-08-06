=======
Hostery
=======

A command line tool for pushing git snapshots to a web host. Hostery creates a browsable history for a project by uploading selected git commits to an FTP server.

Configure a Repository
======================

``$ hostery init``

Issue this command at the root level of a git repository. You will be prompted
for an FTP host which is stored in a file called `.hostery-config`.

Be sure to add ``.hostery-config`` to your ``.gitignore``.

Usage
=====

``$ hostery mark``

1. Synchronizes with your remote git repository. Hostery will pause to allow you to resolve merge conflicts and the like.
2. Uploads the latest commit to your FTP server at ``ftp_root/branch/commit_hash/``
3. Updates an index file at ``ftp_root/`` linking to all of your "marked" commits alongside an iframe.