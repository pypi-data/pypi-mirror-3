#! /usr/bin/env python

import sys
import optparse
import logging

from twisted.internet import reactor, protocol


USAGE = """
{script_name} [options] CONNECTION_SPEC [ CONNECTION_SPEC... ]

Proxy TCP connections according to each CONNECTION_SPEC.
A CONNECTION_SPEC has the form:

  [ LISTEN_HOST ] ':' LISTEN_PORT '-' [ CONNECT_HOST ] ':' CONNECT_PORT

If either host is absent, it defaults to 127.0.0.1.  Connections
to a LISTEN_PORT initiate a connection to the associated
CONNECT_HOST:CONNECT_PORT.  All stream contents are relayed
bidirectionally.

If --log-level is DEBUG, the contents of the stream are sent to the
log stream.
""".format(script_name = sys.argv[0])


def main(args = sys.argv[1:]):
    connectionspecs = parse_args(args)

    logger = logging.getLogger('main')

    for (listenAddr, connectAddr) in connectionspecs:
        (listenHost, listenPort) = listenAddr
        logger.info(
            'Binding %s to connect to %s.',
            addrRepr(listenAddr),
            addrRepr(connectAddr))

        f = ClientSideFactory(connectAddr)
        reactor.listenTCP(listenPort, f, interface=listenHost)

    reactor.run()


def parse_args(args):
    p = optparse.OptionParser(usage=USAGE)
    p.add_option('-l', '--log-level',
                 type='choice',
                 dest='loglevel',
                 default='INFO',
                 choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
                 help='Set logging level.')
    opts, args = p.parse_args(args)

    if not args:
        p.error('No connection specifications given.')

    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s %(levelname) 5s %(name)s | %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S%z',
        level=getattr(logging, opts.loglevel))
        
    def parse_connection_spec(spec):
        hostports = spec.split('-')
        if len(hostports) != 2:
            p.error("Expected LISTEN_HOST_PORT '-' CONNECT_HOST_PORT but found: %r" % (spec,))

        listenspec, connectspec = hostports

        def parse_connection_spec(hostport, defaultport=None):
            fields = hostport.split(':')
            if len(fields) != 2:
                p.error("Expected listen specification of [ HOST ] ':' PORT but found: %r" % (hostport,))
            host, portstr = fields
            if portstr == '' and defaultport is not None:
                port = defaultport
            else:
                try:
                    port = int(portstr)
                except ValueError, e:
                    p.error('Could not parse PORT %r: %r' % (portstr, e.args[0]))
            return (host, port)
                        
        lhost, lport = parse_connection_spec(listenspec)
        chostport = parse_connection_spec(connectspec, lport)

        return ((lhost, lport), chostport)

    return [parse_connection_spec(arg) for arg in args]


class PeerProtocol (protocol.Protocol):

    def __init__(self):
        self._peer = None
        self._reinitLogger()

    # Peer interface:
    def getRemoteAddressRepr(self):
        if self.transport is not None:
            return addrRepr(self.transport.getPeer())
        else:
            return '(n/a)'
        
    def setPeerProtocol(self, protocol):
        self._peer = protocol

    def peerLostConnection(self):
        if self.transport is not None:
            self.transport.loseConnection()
            self.transport = None

    # Twisted Events:
    def connectionMade(self):
        self._peer.setPeerProtocol(self)
        self._reinitLogger()
        self._logger.debug('Connected to peer.')

    def dataReceived(self, data):
        self._peerWrite(data)

    def connectionLost(self, reason):
        self._logger.info('Connection lost.')
        if self._peer is not None:
            self._peer.peerLostConnection()

    # Private:
    def _reinitLogger(self):
        peerAddr = '(n/a)'
        if self._peer is not None:
            peerAddr = self._peer.getRemoteAddressRepr()

        self._logger = logging.getLogger(
            '%s: %s - %s' % (
                type(self).__name__,
                self.getRemoteAddressRepr(),
                peerAddr))

    def _peerWrite(self, data):
        self._logger.debug('Sending: %r', data)
        self._peer.transport.write(data)


class ClientSideProtocol (PeerProtocol):

    def __init__(self):
        PeerProtocol.__init__(self)
        self._inbuf = ''

    # Peer interface:
    def setPeerProtocol(self, protocol):
        PeerProtocol.setPeerProtocol(self, protocol)
        self._reinitLogger()
        self._logger.info('Connection established.')
        self._peerWrite(self._inbuf)
        self._inbuf = None

    # Twisted events:
    def connectionMade(self):
        f = ServerSideFactory(self)
        (host, port) = self.factory.serverAddress
        reactor.connectTCP(host, port, f)

    def dataReceived(self, data):
        if self._peer is None:
            self._inbuf += data
        else:
            PeerProtocol.dataReceived(self, data)


class ClientSideFactory (protocol.Factory):

    protocol = ClientSideProtocol

    def __init__(self, serverAddress):
        self.serverAddress = serverAddress


class ServerSideFactory (protocol.ClientFactory):

    def __init__(self, clientproto):
        self._clientproto = clientproto

    # Twisted events:
    def buildProtocol(self, addr):
        p = PeerProtocol()
        p.setPeerProtocol(self._clientproto)
        return p


def addrRepr(addr):
    if type(addr) is not tuple:
        addr = (addr.host, addr.port)
    return '%s:%d' % addr


if __name__ == '__main__':
    main()
