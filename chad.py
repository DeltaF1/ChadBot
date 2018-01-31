# -*- coding: UTF-8 -*-

import time, re, random
import threading
from queue import Queue
import json

from fbchat import Client
from fbchat.models import *

import thesaurus





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
    match = virgin_re.match(message_object.text.lower())

    if match:
        word = match.group(1)
        synonyms = thesaurus.get_synonyms(word)

        try:
            chadlier = random.choice(synonyms)
        except IndexError:
            return

        if chadlier:

            response = "THE CHAD {}".format(chadlier.upper())
        
            #self.send(Message(text=response), thread_id=thread_id, thread_type=thread_type)

            
            responses.put((response, thread_id, thread_type))
    elif message_object.text == "STOP IT CHAD":
        responses.put(("Ouch!", thread_id, thread_type))
        #self.send(Message(text="Ouch!"), thread_id=thread_id, thread_type=thread_type)
        self.stopListening()
        
    elif message_object.text.lower().startswith("@chad"):
        match = dice_re.search(text.lower())
        
        
        
        if match:
            num_dice = int(match.group(1))
            dice_type = int(match.group(2))
            if match.group(3):
                constant = int(match.group(3))
            else:
                constant = 0
            
            total = 0
            if num_dice > 0 and num_dice < 200:
                for i in range(num_dice):
                    total += random.randint(1, dice_type)
            
            total += constant
            
            user = self.fetchUserInfo(author_id)[author_id]
            
            print("Rolling dice for " + (user.nickname or user.first_name))
            
            name = "@"+(user.nickname or user.first_name)
            
            response = name + " rolled "+str(total)
            
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
    dice_re = re.compile("roll ([0-9]+)d([0-9])+(?: *\+ *([0-9]+))?")
    
    responses = Queue()
    
    chad = Chad(config["facebook"]["email"], config["facebook"]["password"])

    response_thread = threading.Thread(target=response_loop)
    response_thread.daemon = True

    response_thread.start()

    chad.listen()

    time.sleep(5)

    chad.logout()
