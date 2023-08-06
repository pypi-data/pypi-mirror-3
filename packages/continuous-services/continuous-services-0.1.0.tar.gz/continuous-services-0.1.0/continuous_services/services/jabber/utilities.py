import xmpp
import socket
from django.conf import settings

def get_connection():
    jid = xmpp.JID(settings.JABBER_JID)
    user, server = jid.getNode(), jid.getDomain()
    
    client = xmpp.Client(server)
    
    try:
        client.connect(server=(settings.JABBER_SERVER, 5223))
    except socket.error, e:
        raise JabberConnectionFailed(str(e))
    
    auth_result = client.auth(user, settings.JABBER_PASSWORD, "Continuous")
    
    if not auth_result:
        raise JabberAuthFailed()
    
    return client


class JabberConnectionFailed(Exception): pass
class JabberAuthFailed(Exception): pass