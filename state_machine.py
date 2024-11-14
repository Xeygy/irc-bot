from datetime import datetime
from time import sleep
import threading

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

def run_fsm():
    fsm = MyFSM()
    sleeps = [5, 1, 1]
    while True:
        fsm.progress()
        input("")

if __name__=="__main__":
    run_fsm()
