# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.bender.quote import QuoteTrigger
import datetime
import gocept.bender.bot
import mock
import unittest
import zope.event


class QuoteTriggerTest(unittest.TestCase):

    def test_should_not_talk_twice_within_time_threshold(self):
        bender = mock.Mock()
        trigger = QuoteTrigger(bender)
        trigger.join_wait = 0
        trigger.min_silence_duration = datetime.timedelta(minutes=1)
        trigger.speaking_probability = 1.0
        trigger.min_human_messages = 0
        trigger.maybe_say_something()
        trigger.maybe_say_something()
        self.assertEqual(1, bender.say.call_count)

    def test_should_not_talk_until_humans_have_said_enough(self):
        bender = mock.Mock()
        trigger = QuoteTrigger(bender)
        trigger.join_wait = 0
        trigger.speaking_probability = 1.0
        trigger.min_silence_duration = datetime.timedelta(minutes=0)
        trigger.min_human_messages = 1

        trigger.maybe_say_something()
        self.assertFalse(bender.say.called)

        msg = mock.Mock()
        msg.getType.return_value = 'groupchat'
        msg.getFrom().getResource.return_value = 'some_human'
        zope.event.notify(gocept.bender.interfaces.MessageReceivedEvent(msg))

        trigger.maybe_say_something()
        self.assertTrue(bender.say.called)
