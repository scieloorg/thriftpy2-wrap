#coding: utf-8
from __future__ import absolute_import

import logging
import argparse
import socket
import errno
import os
import sys

from thriftpy.protocol import TBinaryProtocolFactory
from thriftpy.server import TThreadedServer
from thriftpy.thrift import TProcessor
from thriftpy.transport import (TBufferedTransportFactory, TServerSocket, )

__all__ = ['ConsoleApp']

_ADDRESS_FAMILY = [af for af in dir(socket) if af.startswith('AF_')]
_DEFAULT_DESCRIPTION = 'Thrift-based RPC server.'
_PROTO_FACTORY = TBinaryProtocolFactory
_TRANS_FACTORY = TBufferedTransportFactory

logger = logging.getLogger(__name__)


def get_description(handler, default=None):
    default_description = default or _DEFAULT_DESCRIPTION
    return handler.__description__ if hasattr(
        handler, '__description__') else default_description


def ConsoleApp(spec, handler,
               proto_factory=_PROTO_FACTORY(),
               trans_factory=_TRANS_FACTORY()):
    def app():
        parser = argparse.ArgumentParser(description=get_description(handler))
        parser.add_argument('--port', type=int, default=8080)
        parser.add_argument('--address-family',
                            type=str,
                            default='AF_INET',
                            choices=sorted(_ADDRESS_FAMILY))
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--host')
        group.add_argument('--unix-socket')
        group.add_argument('--fd', type=int)
        parser.add_argument('--client-timeout', type=float, default=20000,
                help="Timeout in milliseconds for the operation to complete")
        parser.add_argument('--listen-backlog', type=int, default=128,
                help="Queue limit for incomming connections")
        parser.add_argument(
            'arguments',
            default=[],
            nargs='*',
            help="Optional arguments you may need for your app")

        parser.add_argument('--loglevel', default='info', help="log level")
        args = parser.parse_args()

        logging.basicConfig(level=getattr(logging, args.loglevel.upper()))

        address_family = getattr(socket, args.address_family)

        logger.debug('Protocol factory: %s', proto_factory)
        logger.debug('Transport factory: %s', trans_factory)

        server = make_server(spec, handler(*args.arguments),
                             fd=args.fd,
                             host=args.host,
                             port=args.port,
                             unix_socket=args.unix_socket,
                             address_family=address_family,
                             proto_factory=proto_factory,
                             trans_factory=trans_factory,
                             client_timeout=args.client_timeout,
                             backlog=args.listen_backlog)
        try:
            server.serve()
        except KeyboardInterrupt:
            sys.exit(1)
        finally:
            server.close()
            server.trans.close()
            logger.info('Terminating the thrift server')
            logger.debug('Closing transport %s', server.trans)

    return app


def make_server(service, handler,
                fd=None,
                host=None,
                port=None,
                unix_socket=None,
                address_family=socket.AF_INET,
                proto_factory=None,
                trans_factory=None,
                client_timeout=None,
                backlog=128):
    processor = TProcessor(service, handler)
    if unix_socket is not None:
        logger.info('Setting up server bound to %s', unix_socket)
        server_socket = TServerSocket(unix_socket=unix_socket,
                                      socket_family=address_family,
                                      client_timeout=client_timeout,
                                      backlog=backlog)
    elif fd is not None:
        logger.info('Setting up server bound to socket fd %s', fd)
        server_socket = TFDServerSocket(fd=fd,
                                        socket_family=address_family,
                                        client_timeout=client_timeout,
                                        backlog=backlog)
    elif host is not None and port is not None:
        logger.info('Setting up server bound to %s:%s', host, str(port))
        server_socket = TServerSocket(host=host,
                                      port=port,
                                      socket_family=address_family,
                                      client_timeout=client_timeout,
                                      backlog=backlog)
    else:
        raise ValueError('Insufficient params')

    server = TThreadedServer(processor, server_socket,
                             iprot_factory=proto_factory,
                             itrans_factory=trans_factory)
    return server


class TFDServerSocket(TServerSocket):
    def __init__(self, fd=None, **kwargs):
        self._fd = fd
        super(TFDServerSocket, self).__init__(**kwargs)

    def listen(self):
        if self._fd is not None:
            _sock = socket.fromfd(self._fd, self.socket_family, socket.SOCK_STREAM)
            _sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            _sock.setblocking(1)
            self.sock = _sock
        else:
            super(TFDServerSocket, self).listen()

