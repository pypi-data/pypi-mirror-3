=====
mo2s3
=====

A python **command line tool** that simplify **MongoDB backup** (mongodump/mongorestore) **to Amazon S3**.

Stdout/stderr is displayed for each command so if something goes wrong, you can see it immediately.

You can download and restore generated backups yourself **without mo2s3** (just download, untar and mongorestore).

Requirements
============

It makes use of **argparse** for parsing arguments, **mongodump**/**mongorestore**/**tar** with **envoy** and **boto** to upload/download to S3.

* `Envoy <https://github.com/kennethreitz/envoy>`_ python subprocesses for humans
* `Boto <http://pypi.python.org/pypi/boto>`_ to interact with AWS S3
* `Argparse <http://pypi.python.org/pypi/argparse>`_ for parsing command line arguments

Installation
============

    $ pip install mo2s3

You can configure your AWS/MongoDB credentials with mo2s3:

    $ mo2s3 configure

And you can also edit **~/.mo2s3.cfg**.

Usage
=====

Basic usage, mo2s3 -h to show the help.


List bucket files
-----------------

    $ mo2s3 list


Perform Backup
--------------

    $ mo2s3 backup

    $ mo2s3 backup --db mydb


Restore
-------

    $ mo2s3 restore --filename mongodump_20120610235933.tgz

    $ mo2s3 restore --host anotherhost.com:27017 --db mydb --filename mongodump_mydb_20120611150815.tgz


Delete backup
-------------

    $ mo2s3 delete --filename mongodump_20120610235933.tgz

Delete all backups
------------------

    $ mo2s3 drop


How It Works
============

Here is how a **backup** is performed:

1. Run mongodump on the current directory
2. Create tgz of the dump with tar
3. Upload to S3 with boto
4. Delete every generated file

And to **restore**:

1. Download archive from S3
2. Untar to current directory
3. Mongorestore the dump
4. Delete every downloaded file


License (MIT)
=============

Copyright (c) 2012 Thomas Sileo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.