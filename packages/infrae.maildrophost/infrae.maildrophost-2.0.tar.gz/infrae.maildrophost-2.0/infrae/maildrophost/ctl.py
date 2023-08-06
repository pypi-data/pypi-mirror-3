# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: ctl.py 50141 2012-08-23 12:13:03Z sylvain $

import subprocess
import os, signal, sys
import pkg_resources


def maildrop_start(configuration, pidfile):
    """Start maildrophost.
    """
    requirement = list(pkg_resources.parse_requirements(
            'Products.MaildropHost'))[0]
    distribution = pkg_resources.working_set.find(requirement)
    if distribution is None:
        print>>sys.stderr, 'Could not find MaildropHost egg.'
        sys.exit(1)
    script = os.path.join(
            distribution.location,
            'Products',
            'MaildropHost',
            'maildrop',
            'maildrop.py')
    if not os.path.isfile(script):
        print>>sys.stderr, 'Could not find MaildropHost server script.'
        sys.exit(1)
    if not os.path.isfile(configuration):
        print>>sys.stderr, 'Could not find MaildropHost configuration.'
        sys.exit(1)
    subprocess.Popen([sys.executable, script, configuration])


def maildrop_stop(configuration, pidfile):
    """Stop maildrophost.
    """
    if not os.access(pidfile, os.R_OK):
        print>>sys.stderr, "Can't find PID file. Daemon probably not running."
        sys.exit(1)
    try:
        pid = int(open(pidfile).read())
    except ValueError:
        print>>sys.stderr, "Invalid PID file."
        os.unlink(pidfile)
        sys.exit(1)
    os.kill(pid, signal.SIGTERM)
    os.unlink(pidfile)
    print 'Daemon with PID %d stopped.' % pid
    return 0


def maildrop_status(configuration, pidfile):
    """Look after the pid file.
    """
    if os.path.isfile(pidfile):
        try:
            pid = int(open(pidfile).read())
        except ValueError:
            print 'Invalid PID file, unlinking it.'
            os.unlink(pidfile)
        else:
            print 'Daemon with PID %s.' % pid
    else:
        print 'No PID file.'


def usage():
    print "usage: %s [start|stop|restart|status]" % sys.argv[0]
    sys.exit(-255)


def main(options):
    if len(sys.argv) != 2:
        return usage()
    action = sys.argv[1]
    if action == 'start':
        return maildrop_start(**options)
    elif action == 'stop':
        return maildrop_stop(**options)
    elif action == 'restart':
        maildrop_stop(**options)
        return maildrop_start(**options)
    elif action == 'status':
        return maildrop_status(**options)
    return usage()



