=======
Chartio
=======

Chartio utilities for providing read-only user local database access.

Version 1.1.8


Introduction
------------
This project permits Chartio customers to provide database access by
opening an SSH reverse tunnel from a Chartio server to the customer
database.

Errors, comments, questions may be sent to support at chart dot io.


Requirements
------------
Requires a read-only database role (or authorization to create one)
and a local SSH client.

Supported Databases
-------------------
MySQL
PostgreSQL


Installation
------------
To install, type::

    $ python setup.py install

To uninstall, remove the files
    chartio_setup
    chartio_connect


Troubleshooting
-------------
If you encounter an error while running chartio_setup, the file
    /tmp/chartio_error.html
may contain details on what went wrong. In any event, please feel free
to contact support.


Documentation
-------------
Further documentation may be found at http://chart.io/


Package Contents
----------------
    chartio_setup
        The configuration wizard

    chartio_connect
        A script to keep the SSH tunnel alive

Changes
-------
Version 1.1.7
- permit manual entry of database and readonly user/password

Version 1.1.6
- grant 'SHOW VIEW' access when creating mysql read-only database user
- bug fix for handling of blank database administrator password
