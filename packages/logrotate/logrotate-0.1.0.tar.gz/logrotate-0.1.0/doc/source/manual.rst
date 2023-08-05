Manual
++++++

Class
=====

.. automodule:: logrotate 
   :members:
   :undoc-members:

Example
=======

There is an example in the ``test/simple`` directory of the source
distribution. To run it, make sure that the paths, user and group at the top
are specified correctly, and run as root from that directory.

::

    sudo ./run.sh

.. caution ::

   The ``logrotate`` pacakge is fairly new so please don't run the test as root
   without reading through the test first. 

Typical output looks like this:

::

    total 32
    drwxr-xr-x 2 www-data james  4096 2012-01-23 11:10 .
    drwxr-xr-x 3 james    james  4096 2012-01-23 10:23 ..
    -rw-r--r-- 1 james    james   215 2012-01-23 10:24 gen_log_entries.py
    -rw-r--r-- 1 james    james   778 2012-01-23 11:01 logging.conf
    -rwxr-xr-x 1 james    james  1025 2012-01-23 11:05 run.sh
    Traceback (most recent call last):
      File "gen_log_entries.py", line 4, in <module>
        fileConfig('logging.conf')
      File "/usr/lib/python2.6/logging/config.py", line 84, in fileConfig
        handlers = _install_handlers(cp, formatters)
      File "/usr/lib/python2.6/logging/config.py", line 159, in _install_handlers
        h = klass(*args)
      File "/home/james/Documents/Packages/git/logrotate/logrotate/__init__.py", line 88, in __init__
        raise Exception('No such log file %r. Please create it with the permissions you want the rotated files to have'%filename)
    Exception: No such log file 'test.log'. Please create it with the permissions you want the rotated files to have
    total 32
    drwxr-xr-x 2 www-data james  4096 2012-01-23 11:10 .
    drwxr-xr-x 3 james    james  4096 2012-01-23 10:23 ..
    -rw-r--r-- 1 james    james   215 2012-01-23 10:24 gen_log_entries.py
    -rw-r--r-- 1 james    james   778 2012-01-23 11:01 logging.conf
    -rwxr-xr-x 1 james    james  1025 2012-01-23 11:05 run.sh
    total 32
    drwxr-xr-x 2 www-data james  4096 2012-01-23 11:10 .
    drwxr-xr-x 3 james    james  4096 2012-01-23 10:23 ..
    -rw-r--r-- 1 james    james   215 2012-01-23 10:24 gen_log_entries.py
    -rw-r--r-- 1 james    james   778 2012-01-23 11:01 logging.conf
    -rwxr-xr-x 1 james    james  1025 2012-01-23 11:05 run.sh
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log
    Traceback (most recent call last):
      File "gen_log_entries.py", line 4, in <module>
        fileConfig('logging.conf')
      File "/usr/lib/python2.6/logging/config.py", line 84, in fileConfig
        handlers = _install_handlers(cp, formatters)
      File "/usr/lib/python2.6/logging/config.py", line 159, in _install_handlers
        h = klass(*args)
      File "/home/james/Documents/Packages/git/logrotate/logrotate/__init__.py", line 108, in __init__
        raise Exception('The log files %r have different permissions from %r' % (', '.join(failed), self.baseFilename))
    Exception: The log files '/home/james/Documents/Packages/git/logrotate/test/simple/test.log.1, /home/james/Documents/Packages/git/logrotate/test/simple/test.log.2, /home/james/Documents/Packages/git/logrotate/test/simple/test.log.3, /home/james/Documents/Packages/git/logrotate/test/simple/test.log.4, /home/james/Documents/Packages/git/logrotate/test/simple/test.log.5, /home/james/Documents/Packages/git/logrotate/test/simple/test.log.6, /home/james/Documents/Packages/git/logrotate/test/simple/test.log.7, /home/james/Documents/Packages/git/logrotate/test/simple/test.log.8' have different permissions from '/home/james/Documents/Packages/git/logrotate/test/simple/test.log'
    rwxr-xr-x 2 www-data james     4096 2012-01-23 11:10 .
    drwxr-xr-x 3 james    james     4096 2012-01-23 10:23 ..
    -rw-r--r-- 1 james    james      215 2012-01-23 10:24 gen_log_entries.py
    -rw-r--r-- 1 james    james      778 2012-01-23 11:01 logging.conf
    -rwxr-xr-x 1 james    james     1025 2012-01-23 11:05 run.sh
    -rw-rw-r-- 1 www-data james        0 2012-01-23 11:10 test.log
    -rw-r--r-- 1 www-data www-data     0 2012-01-23 11:10 test.log.1
    -rw-r--r-- 1 www-data www-data     0 2012-01-23 11:10 test.log.2
    -rw-r--r-- 1 www-data www-data     0 2012-01-23 11:10 test.log.3
    -rw-r--r-- 1 www-data www-data     0 2012-01-23 11:10 test.log.4
    -rw-r--r-- 1 www-data www-data     0 2012-01-23 11:10 test.log.5
    -rw-r--r-- 1 www-data www-data     0 2012-01-23 11:10 test.log.6
    -rw-r--r-- 1 www-data www-data     0 2012-01-23 11:10 test.log.7
    -rw-r--r-- 1 www-data www-data     0 2012-01-23 11:10 test.log.8
    total 32
    drwxr-xr-x 2 www-data james  4096 2012-01-23 11:10 .
    drwxr-xr-x 3 james    james  4096 2012-01-23 10:23 ..
    -rw-r--r-- 1 james    james   215 2012-01-23 10:24 gen_log_entries.py
    -rw-r--r-- 1 james    james   778 2012-01-23 11:01 logging.conf
    -rwxr-xr-x 1 james    james  1025 2012-01-23 11:05 run.sh
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log.1
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log.2
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log.3
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log.4
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log.5
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log.6
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log.7
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log.8
    -rw-rw-r-- 1 www-data james     0 2012-01-23 11:10 test.log.9
    Printing log entries for [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    total 72
    drwxr-xr-x 2 www-data james  4096 2012-01-23 11:10 .
    drwxr-xr-x 3 james    james  4096 2012-01-23 10:23 ..
    -rw-r--r-- 1 james    james   215 2012-01-23 10:24 gen_log_entries.py
    -rw-r--r-- 1 james    james   778 2012-01-23 11:01 logging.conf
    -rwxr-xr-x 1 james    james  1025 2012-01-23 11:05 run.sh
    -rw-rw-r-- 1 www-data james    48 2012-01-23 11:10 test.log
    -rw-rw-r-- 1 www-data james    48 2012-01-23 11:10 test.log.1
    -rw-rw-r-- 1 www-data james    47 2012-01-23 11:10 test.log.2
    -rw-rw-r-- 1 www-data james    47 2012-01-23 11:10 test.log.3
    -rw-rw-r-- 1 www-data james    47 2012-01-23 11:10 test.log.4
    -rw-rw-r-- 1 www-data james    47 2012-01-23 11:10 test.log.5
    -rw-rw-r-- 1 www-data james    47 2012-01-23 11:10 test.log.6
    -rw-rw-r-- 1 www-data james    47 2012-01-23 11:10 test.log.7
    -rw-rw-r-- 1 www-data james    47 2012-01-23 11:10 test.log.8
    -rw-rw-r-- 1 www-data james    47 2012-01-23 11:10 test.log.9
   
Notice that if the logfile you specify is not there you get an error. If it is
there but the other required files are not, they are automatically created. If
the rotatable log files don't match the permission of the log file specified,
you get the second error.

Finally if everything works, the logs get rotated correctly.
