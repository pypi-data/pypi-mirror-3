##############################################################################
#
# Copyright (c) 2005-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Zope 3 Monitor Server
"""

import errno, logging, os, stat, traceback, socket

import zope.component

import zc.monitor.interfaces

INTERACTIVE_MARKER = object()
QUIT_MARKER = object()
MORE_MARKER = object()

class Server:

    last_command = None

    def __init__(self, connection):
        import zc.ngi.adapters
        connection = zc.ngi.adapters.Lines(connection)
        self.connection = connection
        connection.set_handler(self)
        self.mode = QUIT_MARKER

    def handle_input(self, connection, data):
        args = data.strip().split()
        if self.mode is MORE_MARKER:
            command_name = self.last_command[0]
        elif not args:
            if self.last_command is not None:
                command_name, args = self.last_command
            else:
                return
        else:
            command_name = args.pop(0)
            self.last_command = (command_name, args)
        command = zope.component.queryUtility(
            zc.monitor.interfaces.IMonitorPlugin,
            command_name)
        if command is None:
            connection.write(
                'Invalid command %r\nTry "help".\n' % command_name)
        else:
            try:
                res = command(connection, *args)
            except Exception, v:
                traceback.print_exc(100, connection)
                print >> connection, "%s: %s\n" % (v.__class__.__name__, v)
            else:
                if res in (INTERACTIVE_MARKER, QUIT_MARKER, MORE_MARKER):
                    self.mode = res

        if self.mode is QUIT_MARKER:
            connection.write(zc.ngi.END_OF_DATA)

    def handle_close(self, connection, reason):
        pass                            # Don't care

#testing support
last_listener = None

def start(address):
    """start monitor server.

    Returns the listener address (which may be different from the
    given address) if monitor server started; returns False if the
    port is already in use; and raises an exception otherwise.
    """
    import zc.ngi.async

    ourAddress = None
    if isinstance(address, int):
        #a port is passed as int
        ourAddress = ('', address)
    elif isinstance(address, tuple):
        #an (address, port) tuple is passed
        ourAddress = address
    elif isinstance(address, basestring):
        #a unix domain socket string is passed
        ourAddress = address
        if os.path.exists(ourAddress):
            m = os.stat(ourAddress)
            if stat.S_ISSOCK(m.st_mode):
                os.unlink(ourAddress)

    try:
        global last_listener
        last_listener = zc.ngi.async.listener(ourAddress, Server)
    except socket.error, e:
        if e.args[0] == errno.EADDRINUSE:
            # Don't kill the process just because somebody else has our port.
            # This might be a zopectl debug or some other innocuous problem.
            # (Existing Unix-domain sockets are removed before binding, so
            # this doesn't work that way for those.  Use a separate offline
            # configuration in that case.)
            logging.warning(
                'unable to start zc.monitor server because the address %s '\
                'is in use.',
                ourAddress)
            return False
        else:
            raise
    return last_listener.address

# default commands

def interactive(connection):
    """Turn on monitor's interactive mode

    Normally, the monitor releases the connection after a single command.
    By entering the interactive mode, the monitor will not end the connection
    until you enter the "quit" command.

    In interactive mode, an empty line repeats the last command.
    """
    connection.write('Interactive mode on.  Use "quit" To exit.\n')
    return INTERACTIVE_MARKER

def quit(connection):
    """Quit the monitor

    This is only really useful in interactive mode (see the "interactive"
    command).
    """
    connection.write('Goodbye.\n')
    return QUIT_MARKER

def help(connection, command_name=None):
    """Get help about server commands

    By default, a list of commands and summaries is printed.  Provide
    a command name to get detailed documentation for a command.
    """
    if command_name is None:
        connection.write(str(
            "Supported commands:\n  "
            + '\n  '.join(sorted(
                "%s -- %s" % (name, (u.__doc__ or '?').split('\n', 1)[0])
                for (name, u) in
                zope.component.getUtilitiesFor(
                    zc.monitor.interfaces.IMonitorPlugin)))
            + '\n'))
    else:
        command = zope.component.getUtility(
            zc.monitor.interfaces.IMonitorPlugin,
            command_name)
        connection.write("Help for %s:\n\n%s\n"
                         % (command_name, command.__doc__)
                         )

def register(command, name=None):
    if name is None:
        name = command.__name__
    zope.component.provideUtility(
        command, zc.monitor.interfaces.IMonitorPlugin, name)

def register_basics():
    register(help)
    register(interactive)
    register(quit)
