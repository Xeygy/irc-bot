import random
import re
import socket
import sys
import time

from state_machine import GreetingProtocol
from office_hours import query_oh
from lolFacts import LolFacts

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

        self.irc.settimeout(20)

        # Perform user authentication
        self.command("USER " + botnick + " " + botnick +" " + botnick + " :python")
        self.command("NICK " + botnick)
        #self.irc.send(bytes("NICKSERV IDENTIFY " + botnickpass + " " + botpass + "\n", "UTF-8"))
        time.sleep(5)

        # join the channel
        self.command("JOIN " + channel)
 
    def get_response(self):
        try:
            time.sleep(1)
            # Get the response
            resp = self.irc.recv(2040).decode("UTF-8")
    
            if resp.find('PING') != -1:
                self.command('PONG ' + resp.split()[1]  + '\r') 
    
            return resp
        except socket.timeout:
            return "TIMEOUT: No response \n"

## IRC Config
server = "irc.libera.chat" 	# Provide a valid server IP/Hostname
port = 6667
channel = "#csc482"
botnick = "hello-world-bot"
botnickpass = ""		# in case you have a registered nickname 		
botpass = ""			# in case you have a registered bot	

def getUsername(text: str) -> str:
    return text[1:text.index("!")]

def getMessage(text: str) -> str:
    return text[text.index(f"{botnick}:") + len(botnick) + 1:]


def basicCommands(irc: IRC, username: str, message: str, currentUsers: set, grace, greetingProtocol: GreetingProtocol, lolFacts: LolFacts):
    waitBeforeSending()
    if "die" in message:
        irc.send(channel, f"{username}: Alright then. It was nice knowing you.")
        irc.command("QUIT")
        sys.exit()

    elif "forget" in message:
        greetingProtocol.restart()
        irc.send(channel, f"{username}: Forgetting Everything.")

    elif ("who are you?" in message or "usage" in message):
        irc.send(channel, f"{username}: My name is {botnick}. I was created by Xiuyuan Qiu and Kevin Tan for CSC-482-01 and CSC-482-02.")

        lolMessage1 = f"{username}: One feature I have is to give you some fun facts about League of Legends champions. Along with some champion trivia facts, I can also give you champion answers for the game Loldle, https://loldle.net/classic. Implemented by Kevin Tan."
        lolMessage2 = f"{username}: The Loldle feature just tells you what the answer would be for any champion in the game (Updated up to Aurora), not play the game for you. But it does tell you some demographic information about champions if want are curious abnout that."
        lolMessage3 = f"{username}: Just make sure to mention either LoL or League of Legends anywhere in the command. Also mention fun fact, Loldle, or both in the command for what you want. If not specified I'll just tell you a fun fact. Don't worry about spelling either, I'll try my best to understand anything close."
        lolMessage4 = f"{username}: Ex: [{botnick}: Do you know a fun fact and the Loldle answer for the League of Legends champion Vi.] [{botnick}: Hey I want to know more about the LoL champions Azir and Caitlyn.] [{botnick}: I like the Lol champion Victor.]"

        ohMessage1 = f"{username}: I can also tell you the current office hours/office locations/emails of CSC professors. Ask me a question like `!oh What is Fooad's hours?`, or `!oh beard email`, or `!oh where is dr ventura's room?`. Use prefix `!oh`. (Xiuyuan Qiu)"

        irc.send(channel, lolMessage1)
        waitBeforeSending()
        irc.send(channel, lolMessage2)
        waitBeforeSending()
        irc.send(channel, lolMessage3)
        waitBeforeSending()
        irc.send(channel, lolMessage4)
        waitBeforeSending()
        irc.send(channel, ohMessage1)

    elif ("lol" in message.lower() or "league of legends" in message.lower()):
        responses = lolFacts.interpretMessage(message)
        for response in responses:
            irc.send(channel, f"{username}: {response}")
            waitBeforeSending()
    
    elif "users" in message:
        currentUsersStr = ""
        for user in sorted(currentUsers):
            currentUsersStr += user
            currentUsersStr += ", "
        irc.send(channel, f"{username}: {currentUsersStr[:-2]}")
        print(currentUsers)
    
    elif ("hello" in message or "hi" in message):
        if grace:
            irc.send(channel, f"{username}: {"Sorry can't talk right now. Get back to me in a moment"}")
        else:
            if not greetingProtocol.conversation and not greetingProtocol.finished:
                # Start greeting protocol as speaker 2
                irc.send(channel, f"{username}: {greetingProtocol.beginConvo(2, username)}")
            else:
                irc.send(channel, f"{username}: Hello World!")

    elif message.lower().strip().startswith(f"!oh"):
        query = message.strip().removeprefix("!oh").strip()
        res = query_oh(query)
        irc.send(channel, f"{username}: {res}")
    else:
        irc.send(channel, f"{username}: I did not understand what you said.")    

def manageCurrentUsers(text: str, currentUsers: set):
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

def waitBeforeSending():
    time.sleep(random.randint(1, 2))

def main():
    greetingProtocol = GreetingProtocol()
    lolFacts = LolFacts()

    irc = IRC()
    irc.connect(server, port, channel, botnick, botpass, botnickpass)

    # Keep track of current users
    currentUsers = set()
    
    start = 0
    grace = True
    while True:
        timeout = False
        text = irc.get_response()
        print("RECEIVED ==> ",text) #:foaad-laptop!~foaad-lap@129.65.232.163 PRIVMSG foaad-bot :what's up?
       
        if start != 0:
            time_passed = time.time() - start

            if grace:
                if time_passed >= 20:
                    grace = False
                    start = time.time()
            else:
                if "TIMEOUT" in text or time_passed >= 20:
                    timeout = True
                    start = time.time()

            print(f"Time Passed - {time_passed}")
            print(f"Grace - {grace}")
            print(f"Timeout - {timeout}")

            # Reset timer
            if botnick+":" in text and not grace:
                start = time.time()

        if "PRIVMSG" in text:
            if channel in text and botnick+":" in text:
                if greetingProtocol.conversation and getUsername(text) == greetingProtocol.convoPartner:
                    # In a conversation with another person or bot 
                    botMessage = greetingProtocol.updateState()
                    if botMessage != "":
                        waitBeforeSending()
                        irc.send(channel, f"{getUsername(text)}: {botMessage}")
                    else:
                        grace = True

                    if greetingProtocol.current_state == greetingProtocol.inquiry_1:
                        pass
                    elif greetingProtocol.current_state == greetingProtocol.inquiry_reply_2:
                        botMessage = greetingProtocol.updateState()
                        if botMessage != "":
                            waitBeforeSending()
                            irc.send(channel, f"{getUsername(text)}: {botMessage}")
                else:
                    basicCommands(irc, getUsername(text), getMessage(text).lower(), currentUsers, grace, greetingProtocol, lolFacts) 
        elif timeout and not grace:
            # Haven't started and finished a conversation
            waitBeforeSending()
            if not greetingProtocol.conversation and not greetingProtocol.finished:
                # Start as speaker 1 in greeting protocol
                random_user = random.choice(list(currentUsers))

                irc.send(channel, f"{random_user}: {greetingProtocol.beginConvo(1, random_user)}")
            # Started a conversation and haven't finished one yet. In middle of convo
            elif greetingProtocol.conversation and not greetingProtocol.finished:
                # Get next state of the conversation timeout is an option of the current state
                irc.send(channel, f"{greetingProtocol.convoPartner}: {greetingProtocol.updateState(timeout=True)}")
        else:
            manageCurrentUsers(text, currentUsers)

            if "JOIN" in text and getUsername(text) == botnick:
                # Start timer
                start = time.time()
                
if __name__=="__main__":
    main()
