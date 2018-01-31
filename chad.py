# -*- coding: UTF-8 -*-

import time, re, random, os, sys
import threading
from queue import Queue
import json

from fbchat import Client
from fbchat.models import *

import thesaurus

#from Markus Jarderot @ https://stackoverflow.com/questions/597476
class Re(object):
  def __init__(self):
    self.last_match = None
  def match(self,pattern,text):
    self.last_match = re.match(pattern,text)
    return self.last_match
  def search(self,pattern,text):
    self.last_match = re.search(pattern,text)
    return self.last_match


def response_loop():
    while True:
        to_send = responses.get()
        
        text=to_send[0]
        
        if type(text) == str:
            text = Message(text=text)
        
        thread_id=to_send[1]
        thread_type=to_send[2]
        
        chad.setTypingStatus(TypingStatus.TYPING, thread_id=thread_id, thread_type=thread_type)

        time.sleep(random.random() + 0.5)
        chad.send(text, thread_id=thread_id, thread_type=thread_type)
        
        
        chad.setTypingStatus(TypingStatus.STOPPED, thread_id=thread_id, thread_type=thread_type)

        

def parse_message(self, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg):
    text = message_object.text
    
    gre = Re()

    if gre.match(virgin_re, text.lower()):
        word = gre.last_match.group(1)
        synonyms = thesaurus.get_synonyms(word)

        try:
            chadlier = random.choice(synonyms)
        except IndexError:
            return

        if chadlier:

            response = "THE CHAD {}".format(chadlier.upper())
        
            #self.send(Message(text=response), thread_id=thread_id, thread_type=thread_type)

            
            responses.put((response, thread_id, thread_type))
    elif author_id == config["facebook"]["owner_uid"] and message_object.text == "STOP IT CHAD":
        responses.put(("Ouch!", thread_id, thread_type))
        #self.send(Message(text="Ouch!"), thread_id=thread_id, thread_type=thread_type)
        self.stopListening()
    elif text == "BEGONE CHAD!":
        exit_message = "Chad strides into the sunset, never to be seen again"
        self.send(Message(text=exit_message, mentions=[Mention(self.uid, 0, len(exit_message))]), thread_id, thread_type)
        self.removeUserFromGroup(self.uid, thread_id)
    elif gre.search(dice_re, text.lower()):
        match = gre.last_match
        num_dice = int(match.group(1) or '1')
        dice_type = int(match.group(2))
        if match.group(3):
            constant = int(match.group(3))
        else:
            constant = 0
        
        total = 0
        if dice_type > 0 and num_dice > 0 and num_dice <= 200:
            for i in range(num_dice):
                total += random.randint(1, dice_type)
        else:
            return
            
        total += constant
        
        user = self.fetchUserInfo(author_id)[author_id]
        
        print("Rolling dice for " + (user.nickname or user.first_name))
        
        name = "@"+(user.nickname or user.first_name)
        
        try:
            #gets the rest of the text following the end of the roll command
            reason = text[match.span()[1]:]
        except IndexError:
            reason = ""
        
        response = name + " rolled " + str(total) + reason
        
        responses.put((Message(text=response, mentions=[Mention(author_id, 0, len(name))]), thread_id, thread_type))
        return

class Chad(Client):
    active = True
    #to do: spawn a new thread for every response
    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg):
        self.markAsDelivered(author_id, thread_id)
        thread = threading.Thread(target=parse_message, args=(self, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg))
        thread.daemon = True
        
        thread.start()
if __name__ == '__main__':
    with open("conf.json", "r") as f:
        config = json.load(f)


    owner_uid = config["facebook"]["owner_uid"]

    virgin_re = re.compile("the virgin (.*)");
    dice_re = re.compile("roll ([0-9]*)d([0-9]+)(?: *\+ *([0-9]+))?")
    
    responses = Queue()
    
    chad = Chad(config["facebook"]["email"], config["facebook"]["password"])

    response_thread = threading.Thread(target=response_loop)
    response_thread.daemon = True

    response_thread.start()

    chad.listen()

    chad.logout()
