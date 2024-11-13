from datetime import datetime
from time import sleep

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
        self.time = datetime.now()

        self.END = Node()
        give_up = Node("i give up fr fr :(", self.END)
        inquiry_reply2 = Node("cool cool.", self.END)
        inquiry_wait2 = GUNode(nextNode=inquiry_reply2, giveUpNode=give_up)
        inquiry_reply1 = Node("cool.", inquiry_wait2)
        inquiry_wait1 = GUNode(nextNode=inquiry_reply1, giveUpNode=give_up)
        outreach_reply = GUNode(nextNode=inquiry_wait1, giveUpNode=give_up)
        outreach2 =  GUNode("heloooo! :3", nextNode=outreach_reply, giveUpNode=give_up)
        outreach1 =  GUNode("hello :)", nextNode=outreach_reply, giveUpNode=outreach2)
        self.START = Node(nextNode=outreach1)
        self.state = self.START 
    
    def progress(self, message=None):
        if self.state == self.END:
            print('ended')
            return
        self.updateState(self.state.nextNode)
        
    def updateState(self, newNode):
        self.state = newNode
        if self.state.message != None:
            print(self.state.message)
        self.time = datetime.now()

    def tick(self):
        if self.state == self.END:
            print('ended')
            return
        diff = datetime.now() - self.time
        seconds_since_last_move = diff.total_seconds()

        state_changed = False
        if isinstance(self.state, GUNode):
            if seconds_since_last_move > self.state.giveUpTime:
                self.updateState(self.state.giveUpNode) 
        else:
            self.updateState(self.state.nextNode)

def run_fsm():
    fsm = MyFSM()
    fsm.tick()
    fsm.progress()
    fsm.tick()
    fsm.progress()
    fsm.tick()
    fsm.progress()
    while True:
        fsm.tick()
        sleep(1)

if __name__=="__main__":
    run_fsm()
