import os
import logging.handlers
from logging.handlers import RotatingFileHandler

class PermissionKeepingLogFileRotator(logging.handlers.RotatingFileHandler):
    """\
    This class takes the same arguments as ``RotatingFileHandler`` and is 
    therefore a drop-in replacement.

    It behaves differently though in that it requires the main log file to
    alredy exist with the permissions you want to give it. All the files to store
    the rotated logs must also exist and have the same permissions as the 
    log file specified.

    Now, rather than removing old log files and creating new ones like 
    ``RotatingFileHandler`` does, this implementation simply uses 
    ``os.rename()`` to rotate the files around, *keeping their permissions*.
 
    This means that if for example you set up your log directory and the
    containing files to be owned by ``www-data`` but have a group that related
    commands can also write too, and that you set the group write permission, you
    can allow both Apache and your scripts to use the same Python logging
    configuration with both able to write to the same logs at the same time, safe
    in the knowledge the the permissions you've set won't change during rotation.

    eg here's a directory structure with the permissions we need:

    ::

        $ ls -la
        total 92
        drwxr-xr-x  2 www-data script   4096 2012-01-19 14:11 .
        drwxr-xr-x 17 user     user      4096 2012-01-19 14:04 ..
        -rw-rw-r--  1 www-data script     48 2012-01-19 14:04 test.log
        -rw-rw-r--  1 www-data script     48 2012-01-19 14:04 test.log.1
        -rw-rw-r--  1 www-data script     47 2012-01-19 14:04 test.log.2
        -rw-rw-r--  1 www-data script     47 2012-01-19 14:04 test.log.3
        -rw-rw-r--  1 www-data script     47 2012-01-19 14:04 test.log.4
        -rw-rw-r--  1 www-data script     47 2012-01-19 14:04 test.log.5
        -rw-rw-r--  1 www-data script     47 2012-01-19 14:04 test.log.6
        -rw-rw-r--  1 www-data script     47 2012-01-19 14:04 test.log.7
        -rw-rw-r--  1 www-data script     47 2012-01-19 14:04 test.log.8
        -rw-rw-r--  1 www-data script     47 2012-01-19 14:04 test.log.9


    And here's a suitable logging configuration:

    ::

        # Logging configuration
        [loggers]
        keys = root, script
        
        [handlers]
        keys = console, file
        
        [formatters]
        keys = generic
        
        [logger_root]
        level = WARNING
        handlers = console, file
        
        [logger_script]
        level = INFO
        handlers = file
        qualname = script
        propagate = 0
        
        [handler_console]
        class = StreamHandler
        args = (sys.stderr,)
        level = NOTSET
        formatter = generic
        
        [handler_file]
        class = logrotate.PermissionKeepingLogFileRotator
        formatter = generic
        level = NOTSET
        args = ("test.log", "a", 200000, 9)
        
        [formatter_generic]
        format = %(asctime)s %(levelname)-5.5s [%(name)s] %(message)s

    """
    def __init__(self, filename, *k, **p):
        if not os.path.exists(filename):
            raise Exception('No such log file %r. Please create it with the permissions you want the rotated files to have'%filename)
        RotatingFileHandler.__init__(self, filename, *k, **p)
        # Try to create any missing files
        for i in range(1, self.backupCount):
            log = "%s.%d" % (self.baseFilename, i)
            if not os.path.exists(log):
                fp = open(log, 'w')
                fp.write('')
                fp.close()
        failed = []
        bfst = os.stat(self.baseFilename)
        # Check the key attributes are the same
        for i in range(1, self.backupCount):
            log = "%s.%d" % (self.baseFilename, i)
            st = os.stat(log) 
            for attr in ['mode', 'gid', 'uid']:
                if not getattr(bfst, 'st_'+attr) == getattr(st, 'st_'+attr):
                    failed.append(log)
                    break
        if len(failed) > 1:
            raise Exception('The log files %r have different permissions from %r' % (', '.join(failed), self.baseFilename))
        if len(failed) == 1:
            raise Exception('The log file %r does not have the same permissions as %r' % (', '.join(failed), self.baseFilename))

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """

        self.stream.close()
        if self.backupCount > 0:
            next_log = "%s.tmp" % (self.baseFilename, )
            found_last_file = False
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d" % (self.baseFilename, i)
                dfn = "%s.%d" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    #print "%s -> %s" % (sfn, dfn)
                    if not found_last_file:
                        found_last_file = True
                        os.rename(
                            "%s.%d" % (self.baseFilename, self.backupCount), 
                            next_log,
                        ) 
                    if os.path.exists(dfn):
                        raise Exception('Cannot remove old file, %s'%dfn)
                    os.rename(sfn, dfn)
            dfn = self.baseFilename + ".1"
            if os.path.exists(dfn):
                raise Exception('Cannot remove old file, %s'%dfn)
            os.rename(self.baseFilename, dfn)
            # The problem here is that there is no file that is correct
            os.rename(next_log, self.baseFilename)
            fp = open(self.baseFilename, 'w')
            fp.write('')
            fp.close()
            # Copy the permissions
            #shutil.copystat(dfn, self.baseFilename)
            ## Copy the group and owner
            #os.chown(self.baseFilename, st.st_uid, st.st_gid)
            ##print "%s -> %s" % (self.baseFilename, dfn)
        self.mode = 'w'
        self.stream = self._open()

logging.handlers.PermissionKeepingLogFileRotator = PermissionKeepingLogFileRotator
