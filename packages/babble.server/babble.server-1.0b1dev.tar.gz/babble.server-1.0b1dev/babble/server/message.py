from time import time
from zope.interface import implements
from OFS.SimpleItem import SimpleItem
from interfaces import IMessage

class Message(SimpleItem):
    """ A message """

    implements(IMessage)

    def __init__(self, message, author, timestamp):
        """ Initialize message 
        """
        self._cleared = False
        self.author = author
        self.text = message
        self.time = timestamp
        self.id = 'message.%s' % time()
        
    def uncleared(self):
        """ Has this message been cleard? """
        return not self._cleared

    def markAsCleared(self):
        """ Mark this message as cleared """
        self._cleared= True
