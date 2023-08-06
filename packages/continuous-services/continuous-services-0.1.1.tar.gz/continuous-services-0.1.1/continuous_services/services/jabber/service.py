import xmpp

from continuous_services.service import Service
from continuous_services.services.jabber.utilities import get_connection

class JabberService(Service):
    
    def build_complete(self):
        """Hook called when a build completes"""
        
        if self.build["result"] == "S" and self.data["errors_only"]:
            return
        
        message = """%s : %s, build %d\n%s""" % (self.build["result_human"].upper(), self.project["name"], self.build["display_id"], self.get_build_url())
        
        conn = get_connection()
        conn.send(xmpp.Message(self.data["jid"], message))
    



