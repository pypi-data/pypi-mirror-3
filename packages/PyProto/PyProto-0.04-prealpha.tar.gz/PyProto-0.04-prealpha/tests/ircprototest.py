#!/usr/bin/env python3

from PyProto.eventloop import EventLoop
from PyProto.protocol import IRC

class IRCTest(IRC.IRCProtocol):
    def command_PRIVMSG(self, sender, command, params):
        message = params[-1]
        if not (message.startswith('\x01') and message.endswith('\x01')):
            return

        if message.find('PING', 1, 5) != -1:
            self.write_line("NOTICE {} :{}".format(sender[0], message))
        elif message.find('VERSION', 1, 8) != -1:
            self.write_line("NOTICE {} :{}".format(sender[0], '\x01VERSION testbot v0.0.0.0.0.0.0.0.1 PyProto test\x01'))
        elif message.find('FINGER', 1, 7) != -1:
            self.write_line("NOTICE {} :{}".format(sender[0], '\x01FINGER ew.\x01'))

event = EventLoop.EventLoop()
instance = IRCTest(event, nick="Elizabot", user="Elizabot", gecos="Shitting dicknipples", host="irc.staticbox.net", port=6667, ipv6=False)
instance.connect()
event.run_forever()
