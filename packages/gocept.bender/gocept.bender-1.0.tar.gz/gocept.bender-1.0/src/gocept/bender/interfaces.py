# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt


class MessageReceivedEvent(object):

    def __init__(self, message):
        self.message = message
