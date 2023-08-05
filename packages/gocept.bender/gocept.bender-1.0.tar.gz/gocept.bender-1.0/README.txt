=============
gocept.bender
=============

Bender is a Jabber-Bot.

Its main functionality is to be always online, joined to a groupchat (MUC), and
to accept messages to say there via HTTP POST. Thus, other systems (e.g.
Nagios, Continuous Integration etc.) can perform Jabber notifications without
having to speak Jabber themselves (and without any join/part noise).

You can tell Bender to say something like this::

    curl -d "Say something" http://user:password@host:port

Quotes
======

Bender also sometimes randomly says things by itself (Bender quotes).
To avoid flooding the channel, there are three thresholds:

- Only say something with a given probability.
- Only say something if we haven't said anything for a given time.
- Only say something if at least a given number of messages from other people
  have been said in the chatroom.


Deployment
==========

Bender is deployed and configured using buildout. Here is an example
configuration file::

    [buildout]
    extends = profiles/prod.cfg

    [config]
    chatroom = my-chat@jabber.org
    jabber_user = bender-user
    jabber_password = secret
    min_silence_duration = datetime.timedelta(minutes=5)
    min_human_messages = 10
    speaking_probability = 1.0 / (10 * 60)
    loglevel = INFO
    http_address = 0.0.0.0:8099
    http_user = bender
    http_password = http_secret
