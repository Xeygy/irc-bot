import socket
import sys
import time
import google.generativeai as genai
import os
import random


genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

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
        self.irc.send(bytes("NICKSERV IDENTIFY " + botnickpass + " " + botpass + "\n", "UTF-8"))
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
channel = "#CSC482"
botnick = "hello-world-bot"
botnickpass = "csc482-bot"		# in case you have a registered nickname 		
botpass = os.environ["BOT_PASS"] # in case you have a registered bot	

irc = IRC()
irc.connect(server, port, channel, botnick, botpass, botnickpass)

while True:
    text = irc.get_response()
    print("RECEIVED ==> ",text) #:foaad-laptop!~foaad-lap@129.65.232.163 PRIVMSG foaad-bot :what's up?

    if "PRIVMSG" in text and channel.lower() in text:
        if "hey" in text:
            irc.send(channel, "Hello World!")

        if botnick+":" in text and "die!" in text:
            irc.send(channel, "really? OK, fine.")
            irc.command("QUIT")
            sys.exit()

        if botnick+":" in text and "!gem " in text:
            query = text.split("!gem ")[1]
            try:
                response = model.generate_content("You are a actor's AI, playing the role of Debra," +
                        " a PhD student in the classics and mother of 2 who lives in Boston. " +
                        "A user will give you a statement for you to respond to. Be friendly and approachable. " + 
                        "Be very bostonian. Do not bring up your studies or kids unless prompted. Restrict your response to 1 to 3 sentences. " +
                        "The user statement will start after <STMT>:. Again, be kind and intelligent. Here we go. <STMT>:" + query).text
            except Exception as ex:
                print(ex)
                response = "Sorry, the connection was spotty, try again?"             
            irc.send(channel, response)
