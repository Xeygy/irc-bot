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
                giveUpTime=None):
        super().__init__(message, nextNode)
        self.giveUpNode = giveUpNode
        if giveUpTime:
            self.giveUpTime = giveUpTime
        else:
            self.giveUpTime = 15

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
        # Memory
        self.speaker = 0
        self.conversation = False
        self.finished = False
        self.convoPartner = ""

        # States
        self.end = Node()

        self.giveup_frustrated = Node(nextNode=self.end)

        self.inquiry_reply_1 = Node(nextNode=self.end)
        self.inquiry_2 = GUNode(nextNode=self.end, giveUpNode=self.giveup_frustrated)

        self.inquiry_temp_1 = Node(nextNode=self.inquiry_reply_1)
        
        self.inquiry_reply_2 = Node(nextNode=self.inquiry_2)
        self.inquiry_1 = GUNode(nextNode=self.inquiry_temp_1, giveUpNode=self.giveup_frustrated)

        self.outreach_reply = GUNode(nextNode=self.inquiry_reply_2, giveUpNode=self.giveup_frustrated)
        self.second_outreach = GUNode(nextNode=self.inquiry_1, giveUpNode=self.giveup_frustrated)
        self.initial_outreach = GUNode(nextNode=self.inquiry_1, giveUpNode=self.second_outreach)
        
        self.current_state = Node()

    def beginConvo(self, speaker: int, partner: str = None):
        self.conversation = True
        self.speaker = speaker
        if partner is not None:
            self.convoPartner = partner

        if speaker == 1:
            self.current_state = self.initial_outreach
        else:
            self.current_state = self.outreach_reply

        return self.executeState()

    def executeState(self):
        if self.current_state == self.initial_outreach:
            return self.getMessage("initial_outreach")
        elif self.current_state == self.second_outreach:
            return self.getMessage("second_outreach")
        elif self.current_state == self.inquiry_1:
            return self.getMessage("inquiry_1")
        elif self.current_state == self.inquiry_reply_1:
            return self.getMessage("inquiry_reply_1")
        elif self.current_state == self.inquiry_temp_1:
            return ""
        elif self.current_state == self.inquiry_2:
            return self.getMessage("inquiry_2")
        elif self.current_state == self.inquiry_reply_2:
            return self.getMessage("inquiry_reply_2")
        elif self.current_state == self.outreach_reply:
            return self.getMessage("outreach_reply")
        elif self.current_state == self.giveup_frustrated:
            self.finished = True
            self.conversation = False
            self.restart()
            return self.getMessage("give_up")
        else:
            self.finished = True
            self.conversation = False
            self.restart()
            return ""

    def updateState(self, timeout: bool = None):
        if timeout:
            if isinstance(self.current_state, GUNode):
                self.current_state = self.current_state.giveUpNode

                return self.executeState()
            else:
                return "Wait"
        else:
            self.current_state = self.current_state.nextNode

            return self.executeState()

    def restart(self):
        self.speaker = 0
        self.conversation = False
        self.finished = False
        self.convoPartner = ""
        self.current_state = Node()

    def getMessage(self, state: str) -> str:
        print(state)

        messages = {
            "initial_outreach": ["Hi!", "Hello"],
            "second_outreach": ["I said Hi!", "Excuse me, hello?", "Anyone there?"],
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
