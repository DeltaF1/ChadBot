# -*- coding: UTF-8 -*-

import time, re, random
import threading
from queue import Queue
import json

from fbchat import Client
from fbchat.models import *

import thesaurus


with open("conf.json", "r") as f:
    config = json.load(f)



owner_uid = config["facebook"]["owner_uid"]

virgin_re = re.compile("the virgin (.*)");

responses = Queue()


def response_loop():
    while True:
        to_send = responses.get()
        
        text=to_send[0]
        thread_id=to_send[1]
        thread_type=to_send[2]
        
        chad.setTypingStatus(TypingStatus.TYPING, thread_id=thread_id, thread_type=thread_type)

        time.sleep(random.random() + 0.5)
        
        chad.send(Message(text=text), thread_id=thread_id, thread_type=thread_type)
        
        chad.setTypingStatus(TypingStatus.STOPPED, thread_id=thread_id, thread_type=thread_type)

            
        

class Chad(Client):
    active = True
    #to do: spawn a new thread for every response
    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg):
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

chad = Chad(config["facebook"]["email"], config["facebook"]["password"])

response_thread = threading.Thread(target=response_loop)
response_thread.daemon = True

response_thread.start()

chad.listen()

time.sleep(5)

chad.logout()
