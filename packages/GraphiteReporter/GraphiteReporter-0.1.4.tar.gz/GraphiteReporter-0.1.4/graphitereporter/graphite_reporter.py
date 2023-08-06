"""
Graphite Reporter

Copyright 2012 SmartReceipt; All Rights Reserved.
"""

__author__ = 'Matt Schartman, mschartman@gmail.com'

import socket
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, error as socket_error
from time import time
from logging import getLogger

# The host/server that the graphite/carbon service runs on
GRAPHITE_HOST = 'localhost'

# Port number that the graphite/carbon service listens on
GRAPHITE_PORT = '2003'

# Protocol that we want to use
GRAPHITE_PROTOCOL = 'tcp'


class GraphiteReporter(object):
    """A graphite reporting tool.

    - Enforces a convention where the category will be
      reporting_key.reporting_host.reporting_name
      This now conforms with https://github.com/SmartReceipt/graphite_reporter_rb

    - Accumulates sent report count over the lifetime of the reporter object
      as default.
    """

    def __init__(self, reporting_key, reporting_name, reporting_host=None,
                 graphite_host=GRAPHITE_HOST, graphite_port=GRAPHITE_PORT,
                 graphite_protocol=GRAPHITE_PROTOCOL):
        self.reporting_key = reporting_key
        self.reporting_name = reporting_name
        self._reporting_host = reporting_host
        self._category = None
        self._socket = None
        self.host = graphite_host
        self.port = int(graphite_port)
        self.protocol = graphite_protocol
        self.accumulated_count = 0

    @property
    def reporting_host(self):
        """Get the reporting host."""
        if self._reporting_host is None:
            hostname = socket.gethostname()
            if hostname.count('.'):
                hostname = hostname[:hostname.index('.')]
            self._reporting_host = hostname
        return self._reporting_host

    @property
    def socket(self):
        """Get the socket."""
        l = getLogger('GraphiteReporter.socket')
        if self._socket is None:
            if self.protocol is 'tcp':
                self._socket = socket.socket(AF_INET, SOCK_STREAM)
            elif self.protocol is 'udp':
                self._socket = socket.socket(AF_INET, SOCK_DGRAM)
            else:
                l.error('Unrecognized GRAPHITE_PROTOCOL: %s, '
                        'defaulting to TCP', self.protocol)
                self._socket = socket.socket(AF_INET, SOCK_STREAM)
            try:
                self._socket.connect((self.host, self.port))
            except socket_error, e:
                l.error("Couldn't connect to %s on port %d, is carbon-agent"
                        ".py running?\n%r", self.host, self.port, e)
                raise
        return self._socket

    @property
    def category(self):
        """Get the graphite category."""
        if self._category is None:
            self._category = '.'.join([self.reporting_key,
                                       self.reporting_host,
                                       self.reporting_name])
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    def reset(self):
        """Reset the accumulated count."""
        self.accumulated_count = 0

    def send(self, count=1, send_time=None):
        """Send to the socket."""
        if send_time is None:
            send_time = time()
        if not isinstance(send_time, int):
            send_time = int(send_time)
        self.accumulated_count += count
        self.socket.send(' '.join([self.category,
                                   str(self.accumulated_count),
                                   str(send_time)]))
