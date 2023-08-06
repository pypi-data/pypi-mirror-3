from __future__ import print_function, unicode_literals

from PyProto.eventloop import EventLoop
from PyProto.splitter import LineSplitter
import os, socket

class IRCProtocol(LineSplitter.LineSplitter):
    def __init__(self, event, **kwargs):
        self.nick = kwargs.get('nick', 'PyProto')
        self.altnick = kwargs.get('nick', 'PyProto')
        self.user = kwargs.get('user', 'PyProto')
        self.irc_hostname = kwargs.get('irc_hostname', '*')
        self.gecos = kwargs.get('gecos', 'PyProto based IRC client/bot')

        self.sent_handshake = False

        super(IRCProtocol, self).__init__(event, **kwargs)
    
    def parse_hostmask(self, host):
        first, sep, sec = host.partition('@')
 
        # If we got nothing, then check if it's a server or a nick
        if not sec:
            # More likely to find one faster going backwards...
            if first.rfind('.') == -1:
                # Nick
                return (first, None, None)
            else:
                # Server
                return (None, None, first)
 
        # look for !
        nick, sep, user = first.partition('!')
        if user == '':
            user = None
 
        host = sec
        return (nick, user, host)

    def parse(self, line):
        if line[0] == ':':
            recv, sep, line = line[1:].partition(' ')
            sender = self.parse_hostmask(recv)
        else:
            sender = (None, None, None) 
 
        # Command/numeric
        command, sep, line = line.partition(' ')
 
        if line == '':
            return (sender, command, None)
 
        # Split out the final param
        params, sep, lastparam = line.partition(':')

        # Split up
        params = params.strip(' ').rstrip(' ').split(' ')
        if lastparam != '':
            params.append(lastparam)
 
        params = tuple(params)

        return (sender, command, params)

    def read_line(self, line):
        sender, command, params = self.parse(line)
        command = command.upper()

        # TODO - other method of dispatching...
        attr = getattr(self, 'command_' + command, None)
        if attr is not None:
            attr(sender, command, params)

        # Create line
        if params[-1].find(' ') != -1:
            lastparam = ':{}'.format(params[-1])
        else:
            lastparam = params[-1]

        if sender[0] is None and sender[2] is not None:
            printfrom = sender[2]
        elif sender == (None, None, None):
            printfrom = '<SERVER>'
        else:
            printfrom = "{}!{}@{}".format(*sender)

        printline = "[{}] <{}> {} {}".format(command, printfrom, ' '.join(params[:-1]), lastparam)
        return super(IRCProtocol, self).read_line(printline)

    def command_PING(self, sender, command, params):
        if params:
            out = ' '.join(params)
        else:
            out = str()

        self.write_line("PONG :{}".format(out))

    def command_NOTICE(self, sender, command, params):
        if self.sent_handshake:
            return

        self.write_line("USER {} {} 8 :{}".format(self.user, self.irc_hostname, self.gecos))
        self.write_line("NICK {}".format(self.nick))

        self.sent_handshake = True

