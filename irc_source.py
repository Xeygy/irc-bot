import socket
import sys
import time
import re

class IRC:
    irc = socket.socket()
  
    def __init__(self):
        # Deefine the socket
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def command(self,msg):
        self.irc.send(bytes(msg + "\n", "UTF-8"))
 
    def send(self, channel, msg):
        # Transfer data
        self.command("PRIVMSG " + channel + " :" + msg)
 
    def connect(self, server, port, channel, botnick, botpass, botnickpass):
        # Connect to the server
        print("Connecting to: " + server)
        self.irc.connect((server, port))

        # Perform user authentication
        self.command("USER " + botnick + " " + botnick +" " + botnick + " :python")
        self.command("NICK " + botnick)
        #self.irc.send(bytes("NICKSERV IDENTIFY " + botnickpass + " " + botpass + "\n", "UTF-8"))
        time.sleep(5)

        # join the channel
        self.command("JOIN " + channel)
 
    def get_response(self):
        time.sleep(1)
        # Get the response
        resp = self.irc.recv(2040).decode("UTF-8")
 
        if resp.find('PING') != -1:
           self.command('PONG ' + resp.split()[1]  + '\r') 
 
        return resp

## IRC Config
server = "irc.libera.chat" 	# Provide a valid server IP/Hostname
port = 6667
channel = "#csc482"
botnick = "hello-world-bot"
botnickpass = ""		# in case you have a registered nickname 		
botpass = ""			# in case you have a registered bot	

def getUsername(text):
    return text[1:text.index("!")]

def getMessage(text):
    return text[text.index(f"{botnick}:") + len(botnick) + 1:]
        
def main():
    irc = IRC()
    irc.connect(server, port, channel, botnick, botpass, botnickpass)

    currentUsers = set()
    
    while True:
        text = irc.get_response()
        print("RECEIVED ==> ",text) #:foaad-laptop!~foaad-lap@129.65.232.163 PRIVMSG foaad-bot :what's up?

        if "PRIVMSG" not in text:
            if "NAMES list" in text:
                list = text[text.index(f"{channel} :") + len(channel) + 2:].split()
                for user in list:
                    if not re.search(r":[A-Za-z]+.libera.chat", user):
                        currentUsers.add(user)
                    else:
                        break

                print(currentUsers)
            elif "JOIN" in text:
                currentUsers.add(getUsername(text))
            elif "QUIT" in text:
                currentUsers.remove(getUsername(text))
        else: # if "PRIVMSG" in text:
            if channel in text and botnick+":" in text:
                message = getMessage(text).lower()

                if "die" in message:
                    irc.send(channel, f"{getUsername(text)}: Alright then. It was nice knowing you.")
                    irc.command("QUIT")
                    sys.exit()
                elif "forget" in message:
                    irc.send(channel, f"{getUsername(text)}: Forgetting Everything.")
                elif ("who are you?" == message or "usage" == message):
                    irc.send(channel, f"{getUsername(text)}: My name is {botnick}. I was created by Xiuyuan Qiu and Kevin Tan for CSC-482-01 and CSC-482-02.")
                    irc.send(channel, f"{getUsername(text)}: I do not yet have a purpose or usage.")
                elif "users" in message:
                    currentUsersStr = ""
                    for user in sorted(currentUsers):
                        currentUsersStr += user
                        currentUsersStr += ", "
                    irc.send(channel, f"{getUsername(text)}: {currentUsersStr[:-2]}")
                    print(currentUsers)
                elif ("hello" in message or "hi" in message):
                    irc.send(channel, f"{getUsername(text)}: Hello World!")
                else:
                    irc.send(channel, f"{getUsername(text)}: I did not understand what you said.")    
                
if __name__=="__main__":
    main()
