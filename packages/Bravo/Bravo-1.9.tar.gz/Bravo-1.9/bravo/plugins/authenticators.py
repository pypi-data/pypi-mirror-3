import random
import sys

from twisted.internet import reactor
from twisted.internet.defer import succeed
from twisted.internet.task import deferLater
from twisted.web.client import getPage
from zope.interface import implements

from bravo.ibravo import IAuthenticator
from bravo.beta.packets import make_packet

class OfflineAuthenticator(object):

    implements(IAuthenticator)

    def handshake(self, protocol, container):
        """
        Handle a handshake with an offline challenge.

        This will authenticate just about anybody.
        """

        packet = make_packet("handshake", username="-")

        # Order is important here; the challenged callback *must* fire before
        # we send anything back to the client, because otherwise we won't have
        # a valid entity ready to use.
        d = deferLater(reactor, 0, protocol.challenged)
        d.addCallback(lambda none: protocol.transport.write(packet))

        return True

    def login(self, protocol, container):
        protocol.username = container.username

        players = min(protocol.factory.limitConnections, 60)

        packet = make_packet("login", protocol=protocol.eid, username="",
            seed=protocol.factory.world.seed, mode=protocol.factory.mode,
            dimension=protocol.factory.world.dimension, unknown=1, height=128,
            players=players)
        protocol.transport.write(packet)

        return succeed(None)

    name = "offline"

server = "http://www.minecraft.net/game/checkserver.jsp?user=%s&serverId=%s"

class OnlineAuthenticator(object):

    implements(IAuthenticator)

    def __init__(self):

        self.challenges = {}

    def handshake(self, protocol, container):
        """
        Handle a handshake with an online challenge.
        """

        challenge = "%x" % random.randint(0, sys.maxint)
        self.challenges[protocol] = challenge

        packet = make_packet("handshake", username=challenge)

        d = deferLater(reactor, 0, protocol.challenged)
        d.addCallback(lambda none: protocol.transport.write(packet))

        return True

    def login(self, protocol, container):
        if protocol not in self.challenges:
            protocol.error("Didn't see your handshake.")
            return

        protocol.username = container.username
        challenge = self.challenges.pop(protocol)
        url = server % (container.username, challenge)

        d = getPage(url.encode("utf8"))
        d.addCallback(self.success, protocol, container)
        d.addErrback(self.error, protocol)

        return d

    def success(self, response, protocol, container):

        if response != "YES":
            protocol.error("Authentication server didn't like you.")
            return

        players = min(protocol.factory.limitConnections, 60)

        packet = make_packet("login", protocol=protocol.eid, username="",
            seed=protocol.factory.world.seed, mode=protocol.factory.mode,
            dimension=protocol.factory.world.dimension, unknown=1, height=128,
            players=players)
        protocol.transport.write(packet)

    def error(self, description, protocol):

        protocol.error("Couldn't authenticate: %s" % description)

    name = "online"

offline = OfflineAuthenticator()
online = OnlineAuthenticator()
