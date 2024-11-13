# pip install irc

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

class IRCBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    # nickname being used, add an underscore 
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(
            self.connection.get_nickname()
        ):
            self.do_command(e, a[1].strip())
        return

    def on_dccmsg(self, c, e):
        # non-chat DCC messages are raw bytes; decode as text
        text = e.arguments[0].decode('utf-8')
        c.privmsg("You said: " + text)

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        sender = e.source.nick
        c = self.connection

        if cmd == "die":
            self.die(f"{sender}: Bet")
        elif cmd == "forget":
            # c.send_raw(sender, "Forgetting Everything")
            c.send_raw("Forgetting Everything")
        elif cmd == "users":
            pass
        elif cmd == "hi" or cmd == "hello":
            pass
        elif cmd == "hi" or cmd == "hello":
            pass
        # elif cmd == "stats":
        #     for chname, chobj in self.channels.items():
        #         c.notice(sender, "--- Channel statistics ---")
        #         c.notice(sender, "Channel: " + chname)
        #         users = sorted(chobj.users())
        #         c.notice(sender, "Users: " + ", ".join(users))
        #         opers = sorted(chobj.opers())
        #         c.notice(sender, "Opers: " + ", ".join(opers))
        #         voiced = sorted(chobj.voiced())
        #         c.notice(sender, "Voiced: " + ", ".join(voiced))
        # elif cmd == "dcc":
        #     dcc = self.dcc_listen()
        #     c.ctcp(
        #         "DCC",
        #         sender,
        #         f"CHAT chat {ip_quad_to_numstr(dcc.localaddress)} {dcc.localport}",
        #     )
        else:
            c.privmsg(sender, "Not understood: " + cmd)

CHANNEL = "#csc482"
NICKNAME = "test-bot"
SERVER = "irc.libera.chat"
PORT = 6667

def main():
    test_bot = IRCBot(CHANNEL, NICKNAME, SERVER, PORT)
    test_bot.start()
        
if __name__=="__main__":
    main()