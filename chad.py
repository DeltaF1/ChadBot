# -*- coding: UTF-8 -*-

import time, re, random, os, sys
import threading
import importlib
import json
import sqlite3

from fbchat import Client
from fbchat.models import *

import datamuse
from utils import *

import database


def parse_message(client, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg):
    if author_id == client.uid:
        return
    
    mute_ts = DB.get_timeout(thread_id, "mute")
    
    diff = ts - mute_ts
    
    #if it's been less than 10 minutes since chad was muted for this channel
    if diff <= (10 * 60 * 1000):
        return
    
    response = None
    response_time = None
    
    text = message_object.text
    
    if not text:
        return
    
    gre = Re()

    if gre.match(virgin_re, text.lower()):
        word = gre.last_match.group(1).strip()
        
        chadlier = DB.get_chad(word)
        
        if not chadlier:
            
            synonyms = datamuse.get_synonyms(word)

            try:
                chadlier = random.choice(synonyms)
            except IndexError:
                return

        if chadlier:
            
            if chadlier == "{{CHAD}}":
                response = "{} IS AS CHADLY AS IT GETS".format(word.upper())
            else:
                response = "THE CHAD {}".format(chadlier.upper())

            response = (response, thread_id, thread_type)
    elif text.lower() == "f":
        
        last_f = DB.get_timeout(thread_id, "f")

        diff = ts - last_f
        
        F_RATE = 20000
        
        if diff > F_RATE:
            response = ("F", thread_id, thread_type)
        else:
            return
        
        DB.set_timeout(thread_id, "f", ts)
        
        print("ts = "+str(ts))
        
    elif text == "STOP IT CHAD":
        client.send(Message(text="Ouch!"), thread_id, thread_type)
        
        DB.set_timeout(thread_id, "mute", ts)
    elif text == "BEGONE CHAD!":
        exit_message = "Chad strides into the sunset, never to be seen again"
        client.send(Message(text=exit_message, mentions=[Mention(client.uid, 0, len(exit_message))]), thread_id, thread_type)
        client.removeUserFromGroup(client.uid, thread_id)
    elif author_id == config["facebook"]["owner_uid"] and text.lower() == "restart chad":
        print("Restarting!")
        client.send(Message(text="*gives firm handshake* Chad will be right back."), thread_id, thread_type)
        os.execv(sys.executable, ['python3'] + sys.argv)
    elif "69" in text or "420" in text:
        response = ("nice", thread_id, thread_type)
    
    #TODO: Will be replaced with "return response" in modules
    if not response:
        return
    
    client.type_message(response[0], response[1], response[2])
    
def threaded(func):  
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        
        thread.start()
    
    return wrapper
    

def run_on_modules(func, *args, break_on_true=False, **kwargs):
    for name in modules:
        module = modules[name]
        if hasattr(module, func):
            try:
                result = getattr(module, func)(*args, **kwargs)
            except Exception as e:
                print("Error in module [{}]: {}".format(name, e))
                continue
            if break_on_true and result:
                break
    
class Chad(Client):
    active = True
    
    @threaded
    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg):
        self.markAsDelivered(author_id, thread_id)
        
        parse_message(self, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg)
        
        run_on_modules("onMessage", self, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg)
        
        run_on_modules("parse_message", self, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg, break_on_true=True)
        """
        for name in modules:
            module = modules[name]
            if hasattr(module, "parse_message"):
                result = module.parse_message(self, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg)
                
                if result:
                    break
        """
    @threaded
    def onFriendRequest(self, from_id, msg):
        print("Got friend request from "+str(from_id))
        run_on_modules("onFriendRequest", self, from_id, msg)
        
    
    @threaded
    def onPeopleAdded(self, mid=None, added_ids=None, author_id=None, thread_id=None, ts=None, msg=None):
        if self.uid in added_ids:
            self.type_message("CHAD IS HERE", thread_id, ThreadType.GROUP)

    def type_message(client, message, thread_id, thread_type, delay=None):
        if type(message) == str:
            message = Message(text=message)
        
        delay = delay or random.random() + 0.5
        
        client.setTypingStatus(TypingStatus.TYPING, thread_id=thread_id, thread_type=thread_type)
        
        time.sleep(delay)
        
        try:
            client.send(message, thread_id=thread_id, thread_type=thread_type)
        except Exception as e:
            print("Error sending message: ", e)
        
        client.setTypingStatus(TypingStatus.STOPPED, thread_id=thread_id, thread_type=thread_type)
        
        return True
            
@threaded
def input_loop():
    while True:
        cmd = input()
        
        if input == "restart":
            os.execv(sys.executable, ['python3'] + sys.argv)
    
if __name__ == '__main__':
    with open("conf.json", "r") as f:
        config = json.load(f)

    owner_uid = config["facebook"]["owner_uid"]

    #setup modules
    #From pycruft @ https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    module_names = [f for f in os.listdir("modules") if os.path.isfile(os.path.join("modules", f))]
    
    modules = {}
    
    for name in module_names:
        parts = os.path.splitext(name)
        
        #If it's not a module
        if parts[1] != ".py":
            continue
            
        modules[parts[0]] = importlib.import_module("modules."+parts[0])
    
    virgin_re = re.compile("the virgin ([\w\s]*)");
    
    
    DB = database.Database("chad.sqlite3")
    
    database_thread = threading.Thread(target = DB.loop)
    database_thread.daemon = True
    database_thread.start()
    
    
    input_loop()
    
    chad = Chad(config["facebook"]["email"], config["facebook"]["password"], user_agent=config["facebook"]["user_agent"])
    
    chad.listen()

    chad.logout()
