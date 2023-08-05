from __future__ import with_statement

from contextlib import closing, nested

import logbook
import zmq


logger = logbook.Logger('zrpc.loadbal')


class LoadBalancer(object):

    """
    Load balance to multiple ZRPC servers using a ``zmq.QUEUE`` device.

    There are two ways to configure this load balancer: the ZeroMQ docs refer
    to these as the 'proxy' and 'broker' models, although I like to think of
    them as asymmetric and symmetric, respectively.

    In the proxy model, the load balancer binds to an input socket and connects
    to a number of output sockets downstream. This means no changes are
    required to the servers that are being load-balanced, but the list of
    servers is fixed; adding or removing servers from the cluster requires that
    you reconfigure and restart the load balancer.

    To create a proxy load balancer, pass a list of addresses as the `output`
    argument:

        >>> loadbal = LoadBalancer('inproc://zrpc',
        ...     ('inproc://worker0', 'inproc://worker1', ...))
        >>> loadbal.run()

    In the broker model, the load balancer binds to two sockets; one for input
    and one for output. This means the ZRPC servers now have to connect into
    the load balancer instead, but they can come and go dynamically without
    restarting the load balancer.

    To create a broker load balancer, pass a single address as the `output`
    argument:

        >>> loadbal = LoadBalancer('inproc://zrpc', 'inproc://zrpc-workers')
        >>> loadbal.run()
    """

    def __init__(self, input, output, context=None):
        self.context = context or zmq.Context.instance()
        self.input = input
        self.output = output

    def run(self, setup_callback=None):
        logger.debug("Listening for requests on {0!r}", self.input)
        input_socket = self.context.socket(zmq.XREP)
        input_socket.bind(self.input)

        output_socket = self.context.socket(zmq.XREQ)
        if hasattr(self.output, '__iter__'):
            logger.debug("Connecting to {0} workers", len(self.output))
            for node in self.output:
                output_socket.connect(node)
        else:
            logger.debug("Listening for workers on {0!r}", self.output)
            output_socket.bind(self.output)

        if setup_callback:
            setup_callback(input_socket, output_socket)

        with nested(logger.catch_exceptions(),
                    closing(input_socket),
                    closing(output_socket)):
            zmq.device(zmq.QUEUE, input_socket, output_socket)
