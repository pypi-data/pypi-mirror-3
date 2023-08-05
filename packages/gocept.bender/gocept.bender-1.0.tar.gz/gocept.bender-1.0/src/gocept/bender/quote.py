# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.bender.bot
import gocept.bender.interfaces
import pkg_resources
import random
import threading
import time
import zope.component
import zope.component.event # enable zope.event / zope.component


class QuoteTrigger(object):

    _continue = True
    min_silence_duration = NotImplemented
    min_human_messages = NotImplemented
    speaking_probability = NotImplemented
    join_wait = 30

    def __init__(self, bender, **kw):
        self.bender = bender
        self.last_spoken = datetime.datetime.min
        self.human_message_count = 0
        self.quotes = pkg_resources.resource_string(
            self.__class__.__module__, 'quote.txt').splitlines()
        self.join_time = time.time()

        zope.component.getSiteManager().registerHandler(
            self.count_human_message)

        for key in [
            'min_silence_duration',
            'speaking_probability',
            'min_human_messages']:
            setattr(self, key, kw.get(key, getattr(self, key)))

    @classmethod
    def start(cls, *args, **kw):
        trigger = cls(*args, **kw)
        thread = threading.Thread(target=trigger.run)
        thread.daemon = True
        thread.start()
        return trigger

    def run(self):
        while self._continue:
            self.maybe_say_something()
            time.sleep(1)

    def stop(self):
        self._continue = False

    @zope.component.adapter(gocept.bender.interfaces.MessageReceivedEvent)
    def count_human_message(self, event):
        # skip backlog messages
        if time.time() - self.join_time < self.join_wait:
            return

        message = event.message
        if message.getType() != 'groupchat':
            return
        if message.getFrom().getResource() == 'bender':
            return
        self.human_message_count += 1

    @property
    def may_speak(self):
        now = datetime.datetime.now()
        return (now > self.last_spoken + self.min_silence_duration
                and self.human_message_count >= self.min_human_messages)

    @property
    def should_speak(self):
        return random.random() < self.speaking_probability

    def maybe_say_something(self):
        if not self.may_speak:
            return
        if self.should_speak:
            self.bender.say(random.choice(self.quotes))
            self.last_spoken = datetime.datetime.now()
            self.human_message_count = 0
