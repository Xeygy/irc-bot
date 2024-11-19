from datetime import datetime
from time import sleep
import threading

class Node:
    def __init__(self, 
                message=None, 
                nextNode=None,
                user_id=None):
        self.message = message
        self.nextNode = nextNode
        self.user_id = user_id

# GiveUppableNode
class GUNode(Node):
    def __init__(self, 
                message=None, 
                nextNode=None, 
                giveUpNode=None,
                giveUpTime=3,
                user_id=None):
        super().__init__(message, nextNode, user_id)
        self.giveUpNode = giveUpNode
        self.giveUpTime = giveUpTime

class MyFSM:
    def __init__(self):
        self.timer = None
        self.END = Node()
        give_up = Node("i give up fr fr :(", self.END)
        inquiry_reply1 = Node("I'm good thanks for asking", self.END, user_id=1)
        inquiry2 = GUNode("and yourself?", inquiry_reply1, give_up, user_id=2)
        inquiry_reply2 = Node("I'm fine", nextNode=inquiry2, user_id=2)
        inquiry1 = GUNode("whats happening", nextNode=inquiry_reply2, giveUpNode=give_up, user_id=1)
        outreach_reply2 = GUNode("hello back at you!", nextNode=inquiry1, giveUpNode=give_up, user_id=2)
        outreach1_2 =  GUNode("excuse me, hello?", nextNode=outreach_reply2, giveUpNode=give_up, user_id=1)
        self.outreach1_1 = GUNode("hello", nextNode=outreach_reply2, giveUpNode=outreach1_2, user_id=1)
        waiter = GUNode(nextNode=outreach_reply2, giveUpNode=self.outreach1_1)
        self.START = Node(nextNode=waiter)
        self.ROLE = 2
        self.state = self.START 
    
    def nrole(self):
        return 1 if self.ROLE == 2 else self.ROLE + 1

    def start(self):
        self.updateState(self.ROLE)

    def progress(self, message=None):
        if self.state == self.END:
            print('ended')
            return
        self.updateState(self.nrole())
        
    def updateState(self, role, nex=None):
        self.state = self.state.nextNode if nex is None else nex
        print(f"       us {role} | {self.ROLE} | {self.state.user_id} | {self.state.message}") # debug
        if self.timer != None:
            self.timer.cancel()
        if self.state.message != None and \
           (self.state.user_id == self.ROLE or self.state.user_id is None):
            print(self.state.message)
        if (isinstance(self.state, GUNode)) and (self.state.user_id == self.ROLE or self.state.user_id is None):
            self.timer = threading.Timer(self.state.giveUpTime, self.give_up)
            self.timer.start()
        # if this state is still the bot, we roll on
        elif (self.state.user_id == role and role == self.ROLE)         \
              and self.state.user_id is not None:    
            print(f"      {self.ROLE}") # debug
            self.updateState(self.state.nextNode.user_id)

    def give_up(self):
        # unclean, but gets the job done
        # if no one messages within a time limit, we assume role 1
        if self.state.giveUpNode == self.outreach1_1:
            self.ROLE = 1
        self.updateState(self.ROLE, self.state.giveUpNode)

def run_fsm():
    fsm = MyFSM()
    fsm.start()
    while True:
        input("")
        fsm.progress()

if __name__=="__main__":
    run_fsm()
