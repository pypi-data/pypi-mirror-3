==============
Monitor Server
==============

The monitor server is a server that provides a command-line interface to
request various bits of information.  The server is zc.ngi based, so we can use
the zc.ngi testing infrastructure to demonstrate it.

    >>> import zc.ngi.testing
    >>> import zc.monitor

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)

The server supports an extensible set of commands.  It looks up
commands as named zc.monitor.interfaces.IMonitorPlugin "utilities", as defined
by the zope.component package.

To see this, we'll create a hello plugin:

    >>> def hello(connection, name='world'):
    ...     """Say hello
    ...
    ...     Provide a name if you're not the world.
    ...     """
    ...     connection.write("Hi %s, nice to meet ya!\n" % name)

and register it:

    >>> zc.monitor.register(hello)

When we register a command, we can provide a name. To see this, we'll
register ``hello`` again:

    >>> zc.monitor.register(hello, 'hi')

Now we can give the hello command to the server:

    >>> connection.test_input('hi\n')
    Hi world, nice to meet ya!
    -> CLOSE

We can pass a name:

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)
    >>> connection.test_input('hello Jim\n')
    Hi Jim, nice to meet ya!
    -> CLOSE

The server comes with a few basic commands.  Let's register
them so we can see what they do.  We'll use the simplfied registration
interface:

    >>> zc.monitor.register_basics()

The first is the help command.  Giving help without input, gives a
list of available commands:

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)
    >>> connection.test_input('help\n')
    Supported commands:
      hello -- Say hello
      help -- Get help about server commands
      hi -- Say hello
      interactive -- Turn on monitor's interactive mode
      quit -- Quit the monitor
    -> CLOSE

We can get detailed help by specifying a command name:

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)
    >>> connection.test_input('help help\n')
    Help for help:
    <BLANKLINE>
    Get help about server commands
    <BLANKLINE>
        By default, a list of commands and summaries is printed.  Provide
        a command name to get detailed documentation for a command.
    <BLANKLINE>
    -> CLOSE

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)
    >>> connection.test_input('help hello\n')
    Help for hello:
    <BLANKLINE>
    Say hello
    <BLANKLINE>
        Provide a name if you're not the world.
    <BLANKLINE>
    -> CLOSE

The ``interactive`` command switches the monitor into interactive mode.  As
seen above, the monitor usually responds to a single command and then closes
the connection.  In "interactive mode", the connection is not closed until
the ``quit`` command is used.  This can be useful when accessing the monitor
via telnet for diagnostics.

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)
    >>> connection.test_input('interactive\n')
    Interactive mode on.  Use "quit" To exit.
    >>> connection.test_input('help interactive\n')
    Help for interactive:
    <BLANKLINE>
    Turn on monitor's interactive mode
    <BLANKLINE>
        Normally, the monitor releases the connection after a single command.
        By entering the interactive mode, the monitor will not end the connection
        until you enter the "quit" command.
    <BLANKLINE>
        In interactive mode, an empty line repeats the last command.
    <BLANKLINE>
    >>> connection.test_input('help quit\n')
    Help for quit:
    <BLANKLINE>
    Quit the monitor
    <BLANKLINE>
        This is only really useful in interactive mode (see the "interactive"
        command).
    <BLANKLINE>

Notice that the result of the commands did not end with "-> CLOSE", which would
have indicated a closed connection.

Also notice that the interactive mode allows you to repeat commands.

    >>> connection.test_input('hello\n')
    Hi world, nice to meet ya!
    >>> connection.test_input('\n')
    Hi world, nice to meet ya!
    >>> connection.test_input('hello Jim\n')
    Hi Jim, nice to meet ya!
    >>> connection.test_input('\n')
    Hi Jim, nice to meet ya!

Now we will use ``quit`` to close the connection.

    >>> connection.test_input('quit\n')
    Goodbye.
    -> CLOSE

Finally, it's worth noting that exceptions will generate a
traceback on the connection.

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)
    >>> connection.test_input('hello Jim 42\n') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: hello() takes at most 2 arguments (3 given)
    <BLANKLINE>
    -> CLOSE

.. Edge cases

   Closing the connection:

   >>> connection.test_close('test')


Command loops
-------------

Using the "MORE" mode, commands can signal that they want to claim all future
user input.  We'll implement a silly example to demonstrate how it works.

Here's a command that implements a calculator.

    >>> PROMPT = '.'
    >>> def calc(connection, *args):
    ...     if args and args[0] == 'quit':
    ...         return zc.monitor.QUIT_MARKER
    ...
    ...     if args:
    ...         connection.write(str(eval(''.join(args))))
    ...         connection.write('\n')
    ...
    ...     connection.write(PROMPT)
    ...     return zc.monitor.MORE_MARKER

If we register this command...

    >>> zc.monitor.register(calc)

...we can invoke it and we get a prompt.

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)
    >>> connection.test_input('calc\n')
    .

If we then give it more input we get the result plus another prompt.

    >>> connection.test_input('2+2\n')
    4
    .

    >>> connection.test_input('4*2\n')
    8
    .

Once we're done we can tell the calculator to let us go.

    >>> connection.test_input('quit\n')
    -> CLOSE

Start server
------------

    >>> import time
    >>> import zope.testing.loggingsupport, logging
    >>> loghandler = zope.testing.loggingsupport.InstalledHandler(
    ...                  None, level=logging.INFO)


    >>> zc.monitor.start(9644)
    ('', 9644)

    >>> print loghandler
    zc.ngi.async.server INFO
      listening on ('', 9644)

    >>> zc.monitor.last_listener.close()
    >>> zc.monitor.last_listener = None
    >>> time.sleep(0.1)

    >>> loghandler.clear()

    >>> zc.monitor.start(('127.0.0.1', 9644))
    ('127.0.0.1', 9644)

    >>> print loghandler
    zc.ngi.async.server INFO
      listening on ('127.0.0.1', 9644)

    >>> zc.monitor.last_listener.close()
    >>> zc.monitor.last_listener = None
    >>> time.sleep(0.1)

Bind to port 0:

    >>> addr = zc.monitor.start(0)
    >>> addr == zc.monitor.last_listener.address
    True

    >>> zc.monitor.last_listener.close()
    >>> zc.monitor.last_listener = None
    >>> time.sleep(0.1)

Trying to rebind to a port in use:

    >>> loghandler.clear()

    >>> zc.monitor.start(('127.0.0.1', 9644))
    ('127.0.0.1', 9644)

    >>> zc.monitor.start(('127.0.0.1', 9644))
    False

    >>> print loghandler
    zc.ngi.async.server INFO
      listening on ('127.0.0.1', 9644)
    zc.ngi.async.server WARNING
      unable to listen on ('127.0.0.1', 9644)
    root WARNING
      unable to start zc.monitor server because the address ('127.0.0.1', 9644) is in use.

    >>> zc.monitor.last_listener.close()
    >>> zc.monitor.last_listener = None
    >>> time.sleep(0.1)

    >>> loghandler.uninstall()
