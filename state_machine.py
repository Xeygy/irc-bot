from datetime import datetime
from time import sleep
import threading
import random

class Node:
    def __init__(self, 
                message=None, 
                nextNode=None):
        self.message = message
        self.nextNode = nextNode

# GiveUppableNode
class GUNode(Node):
    def __init__(self, 
                message=None, 
                nextNode=None, 
                giveUpNode=None,
                giveUpTime=3):
        super().__init__(message, nextNode)
        self.giveUpNode = giveUpNode
        self.giveUpTime = giveUpTime

class MyFSM:
    def __init__(self):
        self.timer = None
        self.END = Node()
        give_up = Node("i give up fr fr :(", self.END)
        inquiry_reply2 = Node("cool cool.", self.END)
        inquiry_wait1 = GUNode(nextNode=inquiry_reply2, giveUpNode=give_up)
        inquiry_reply1 = Node("cool.", inquiry_wait1)
        outreach_reply = GUNode("hello back at you!", nextNode=inquiry_reply1, giveUpNode=give_up)
        outreach2 =  GUNode("heloooo! :3", nextNode=outreach_reply, giveUpNode=give_up)
        outreach1 =  GUNode("hello :)", nextNode=outreach_reply, giveUpNode=outreach2)
        self.START = Node(nextNode=outreach1)
        self.state = self.START 
    
    def progress(self, message=None):
        if self.state == self.END:
            print('ended')
            return
        self.updateState()
        
    def updateState(self, nex=None):
        self.state = self.state.nextNode if nex is None else nex
        if self.timer != None:
            self.timer.cancel()
        if self.state.message != None:
            print(self.state.message)
        if (isinstance(self.state, GUNode)):
            self.timer = threading.Timer(self.state.giveUpTime, self.give_up)
            self.timer.start()
        elif self.state != self.END:
                self.updateState()

    def give_up(self):
        self.updateState(self.state.giveUpNode)

class GreetingProtocol():
    def __init__(self):
        self.initial_outreach = GUNode()
        self.second_outreach = GUNode()
        self.outreach_reply = GUNode()

        self.inquiry_1 = GUNode()
        self.inquriy_reply_1 = Node()
        
        self.inquiry_2 = GUNode()
        self.inquiry_reply_2 = Node()

        self.giveup_frustrated = Node()

        self.state = self.initial_outreach
        self.end = Node("")

        self.conversation = False
        self.finished = False
    
    def start(self, speaker: int):
        self.conversation = True
        
        print(f"Starting Greeting Protocol. Speaker - {speaker}")

    def restart(self):
        self.state = self.initial_outreach

    def getMessage(state: str) -> str:
        messages = {
            "inital_outreach": ["Hi!", "Hello"],
            "second_outreach": ["I said Hi!", "Excuse me, hello?"],
            "outreach_reply": ["Hi", "Hello back at you"],
            "inquiry_1": ["How are you?", "What's happening"],
            "inquiry_2": ["How about you?", "And yourself?"],
            "inquiry_reply_1": ["I'm good", "I'm fine"],
            "inquiry_reply_2": ["I'm good", "I'm fine, thanks for asking"],
            "give_up": ["Ok, forget you.", "Whatever", "I can't with you"],
        }
        
        return random.choice(messages[state])

def run_fsm():
    fsm = MyFSM()
    sleeps = [5, 1, 1]
    while True:
        fsm.progress()
        input("")

if __name__=="__main__":
    run_fsm()
