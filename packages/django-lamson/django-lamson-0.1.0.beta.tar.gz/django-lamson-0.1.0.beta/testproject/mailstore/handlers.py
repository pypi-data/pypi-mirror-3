import re
import logging
from lamson.routing import route, route_like, stateless
from testproject.mailstore.models import ReceivedMessage



@route("(address)@(host)", address=".+")
@stateless
def STORE(message, address=None, host=None):
    msg = ReceivedMessage(from_address = message.base['From'], 
                         to_address = "%s@%s"%(address, host),
                         subject =  message.base['Subject'], 
                         content = message.body())

    msg.save()