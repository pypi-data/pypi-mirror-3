from twisted.internet.defer import fail
from twisted.web.client import getPage

server = "http://www.minecraft.net"

def _check_name_cb(response):
    if response.lower().strip() != "yes":
        return fail()

def _user_paid_cb(response):
    if response.lower().strip() != "true":
        return fail()

def check_name(username, server_hash):
    """
    Verify that a user is who they say they are.
    """

    url = "%s/game/checkserver.jsp?user=%s&serverId=%s"
    url = url % (server, username, server_hash)

    d = getPage(url.encode("utf8"))
    d.addCallback(_check_name_cb)

    return d

def user_exists(username):
    """
    Verify that a user exists.
    """

    url = "%s/haspaid.jsp?user=%s"
    url = url % (server, username)

    d = getPage(url.encode("utf8"))
    d.addCallback(_user_paid_cb)

    return d
