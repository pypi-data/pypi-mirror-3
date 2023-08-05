# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import Queue
import gocept.bender.http
import gocept.bender.interfaces
import gocept.bender.quote
import jabberbot
import logging
import socket
import sys
import time
import zope.event


log = logging.getLogger(__name__)


class Bender(jabberbot.JabberBot):

    def __init__(self, user, password, chatroom):
        super(Bender, self).__init__(
            user, password, res='bender.' + socket.gethostname())
        self.chatroom = chatroom
        self.join_room(self.chatroom, 'bender')
        log.info('joined %s', self.chatroom)
        self.messages = Queue.Queue()

    def idle_proc(self):
        try:
            message = self.messages.get_nowait()
        except Queue.Empty:
            return super(Bender, self).idle_proc()
        log.info('sending %r to %s', message, self.chatroom)
        self.send(self.chatroom, message, message_type='groupchat')

    def say(self, message):
        self.messages.put(message)

    def callback_message(self, connection, msg):
        # XXX we don't call super at the moment, so botcmd is disabled
        self.__lastping = time.time()
        log.debug('received message %r', (
                msg.getType(), self.get_sender_username(msg),
                msg.getProperties(), msg.getBody()))
        zope.event.notify(
            gocept.bender.interfaces.MessageReceivedEvent(msg))


def main(**kw):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'))
    logging.root.handlers = [handler]
    logging.root.setLevel(getattr(logging, kw['loglevel']))
    bender = Bender(kw['jabber_user'], kw['jabber_password'], kw['chatroom'])
    host, port = kw['http_address'].split(':')
    httpd = gocept.bender.http.HTTPServer.start(
        host, int(port), bender, kw['http_user'], kw['http_password'])
    quote = gocept.bender.quote.QuoteTrigger.start(bender, **kw)
    try:
        bender.serve_forever()
    finally:
        httpd.shutdown()
        quote.stop()
