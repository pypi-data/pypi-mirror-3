##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Server interfaces.
"""

class Attribute(object):
    def __init__(self, title, description=None):
        self.title = title
        self.description = description

class Interface(object):
    pass

class ISocket(Interface):
    """Represents a socket.

    Note: Most of this documentation is taken from the Python Library
    Reference.
    """

    def listen(backlog):
        """Listen for connections made to the socket.

        The 'backlog' argument specifies the maximum number of queued
        connections and should be at least 1; the maximum value is
        system-dependent (usually 5).
        """

    def bind(addr):
        """Bind the socket to address.

        The socket must not already be bound.
        """

    def connect(address):
        """Connect to a remote socket at address."""

    def accept():
        """Accept a connection.

        The socket must be bound to an address and listening for
        connections. The return value is a pair (conn, address) where conn is
        a new socket object usable to send and receive data on the connection,
        and address is the address bound to the socket on the other end of the
        connection.
        """

    def recv(buffer_size):
        """Receive data from the socket.

        The return value is a string representing the data received. The
        maximum amount of data to be received at once is specified by
        bufsize. See the Unix manual page recv(2) for the meaning of the
        optional argument flags; it defaults to zero.
        """

    def send(data):
        """Send data to the socket.

        The socket must be connected to a remote socket. The optional flags
        argument has the same meaning as for recv() above. Returns the number
        of bytes sent. Applications are responsible for checking that all data
        has been sent; if only some of the data was transmitted, the
        application needs to attempt delivery of the remaining data.
        """

    def close():
        """Close the socket.

        All future operations on the socket object will fail. The remote end
        will receive no more data (after queued data is flushed). Sockets are
        automatically closed when they are garbage-collected.
        """


class ITaskDispatcher(Interface):
    """An object that accepts tasks and dispatches them to threads.
    """

    def set_thread_count(count):
        """Sets the number of handler threads.
        """

    def add_task(task):
        """Receives a task and dispatches it to a thread.

        Note that, depending on load, a task may have to wait a
        while for its turn.
        """

    def shutdown(cancel_pending=True, timeout=5):
        """Shuts down all handler threads and may cancel pending tasks.
        """

class ITask(Interface):
    """
    The interface expected of an object placed in the queue of
    a ThreadedTaskDispatcher.  Provides facilities for executing
    or canceling the task.
    """

    def service():
        """
        Services the task.  Either service() or cancel() is called
        for every task queued.
        """

    def cancel():
        """
        Called instead of service() during shutdown or if an
        exception occurs that prevents the task from being
        serviced.  Must return quickly and should not throw exceptions.
        """

    def defer():
        """
        Called just before the task is queued to be executed in
        a different thread.
        """

class IDispatcherEventHandler(Interface):
    """The Dispatcher can receive several different types of events. This
       interface describes the necessary methods that handle these common
       event types.
    """

    def handle_read_event():
        """Given a read event, a server has to handle the event and
           read the input from the client.
        """

    def handle_write_event():
        """Given a write event, a server has to handle the event and
           write the output to the client.
        """

    def handle_expt_event():
        """An exception event was handed to the server.
        """

    def handle_error():
        """An error occurred, but we are still trying to fix it.
        """

    def handle_expt():
        """Handle unhandled exceptions. This is usually a time to log.
        """

    def handle_read():
        """Read output from client.
        """

    def handle_write():
        """Write output via the socket to the client.
        """

    def handle_connect():
        """A client requests a connection, now we need to do soemthing.
        """

    def handle_accept():
        """A connection is accepted.
        """

    def handle_close():
        """A connection is being closed.
        """


class IStreamConsumer(Interface):
    """Consumes a data stream until reaching a completion point.

    The actual amount to be consumed might not be known ahead of time.
    """

    def received(data):
        """Accepts data, returning the number of bytes consumed."""

    completed = Attribute(
        'completed', 'Set to a true value when finished consuming data.')


class IServer(Interface):
    """This interface describes the basic base server.

       The most unusual part about the Zope servers (since they all
       implement this interface or inherit its base class) is that it
       uses a mix of asynchronous and thread-based mechanism to
       serve. While the low-level socket listener uses async, the
       actual request is executed in a thread.  This is important
       because even if a request takes a long time to process, the
       server can service other requests simultaneously.
    """

    channel_class = Attribute("""
                        The channel class defines the type of channel
                        to be used by the server. See IServerChannel
                        for more information.
                              """)

    def getsockname():
        """ Return the IP-address, port number pair to which this server's
        socket is bound"""


class IDispatcherLogging(Interface):
    """This interface provides methods through which the Dispatcher will
       write its logs. A distinction is made between hit and message logging,
       since they often go to different output types and can have very
       different structure.
    """

    def log (message):
        """Logs general requests made to the server.
        """

    def log_info(message, type='info'):
        """Logs informational messages, warnings and errors.
        """


class IServerChannel(Interface):

    parser_class = Attribute("""Subclasses must provide a parser class""")
    task_class = Attribute("""Specifies the ITask class to be used for
                           generating tasks.""")

    def queue_task(task):
        """Queues a channel-related task to be processed in sequence.
        """


class IDispatcher(ISocket, IDispatcherEventHandler, IDispatcherLogging):
    """The dispatcher is the most low-level component of a server.

       1. It manages the socket connections and distributes the
          request to the appropriate channel.

       2. It handles the events passed to it, such as reading input,
          writing output and handling errors. More about this
          functionality can be found in IDispatcherEventHandler.

       3. It handles logging of the requests passed to the server as
          well as other informational messages and erros. Please see
          IDispatcherLogging for more details.

       Note: Most of this documentation is taken from the Python
             Library Reference.
    """

    def add_channel(map=None):
        """After the low-level socket connection negotiation is
           completed, a channel is created that handles all requests
           and responses until the end of the connection.
        """

    def del_channel(map=None):
        """Delete a channel. This should include also closing the
           socket to the client.
        """

    def create_socket(family, type):
        """This is identical to the creation of a normal socket, and
           will use the same options for creation. Refer to the socket
           documentation for information on creating sockets.
        """

    def readable():
        """Each time through the select() loop, the set of sockets is
           scanned, and this method is called to see if there is any
           interest in reading. The default method simply returns 1,
           indicating that by default, all channels will be
           interested.
        """

    def writable():
        """Each time through the select() loop, the set of sockets is
           scanned, and this method is called to see if there is any
           interest in writing. The default method simply returns 1,
           indicating that by default, all channels will be
           interested.
        """

class IHeaderOutput(Interface):
    """Interface for setting HTTP response headers.

    This allows the HTTP server and the application to both set response
    headers.
    """

    def setResponseStatus(status, reason):
        """Sets the status code and the accompanying message.
        """

    def appendResponseHeaders(lst):
        """Sets headers that can potentially repeat.

        Takes a list of strings.
        """

    wrote_header = Attribute(
        """Returns a flag indicating whether the response

        header has already been sent.
        """)

