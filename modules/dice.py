from fbchat.models import *
from utils import *
import random

dice_re = re.compile("roll (?:a )?([0-9]*)d([0-9]+)(?: *\+ *([0-9]+))?")
coin_re = re.compile("flip (a|\d+) coin(?:s?)")

def parse_message(client, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg, escaped_text=""):
    text = escaped_text
    gre = Re()
    
    response = None
    
    if gre.search(dice_re, text.lower()):
        match = gre.last_match
        num_dice = int(match.group(1) or '1')
        dice_type = int(match.group(2))
        if match.group(3):
            constant = int(match.group(3))
        else:
            constant = 0
        
        total = 0
        if dice_type > 0 and dice_type < 10000 and num_dice > 0 and num_dice <= 200:
            for i in range(num_dice):
                total += random.randint(1, dice_type)
        else:
            return
            
        total += constant
        
        name = get_name(client, author_id, thread_id, thread_type)
        
        try:
            #gets the rest of the text following the end of the roll command
            reason = text[match.span()[1]:]
        except IndexError:
            reason = ""
        
        response = name + " rolled " + str(total) + reason
        
        response = (Message(text=response, mentions=[Mention(author_id, 0, len(name))]), thread_id, thread_type)
    elif gre.search(coin_re, text.lower()):
        match = gre.last_match
        
        try:
            num_coins = int(match.group(1))
        except ValueError:
            num_coins = 1
        
        if num_coins == 1:
            result = random.choice(("heads", "tails"))
        elif 0 < num_coins <= 25:
            result = "["
            
            for i in range(num_coins):
                result += random.choice(("H", "T")) + ","
            
            result = result[:-1] + "]"
        else:
            return
        
        name = get_name(client, author_id, thread_id, thread_type)
        
        response = name + " got " + result
        
        response = (Message(text=response, mentions=[Mention(author_id, 0, len(name))]), thread_id, thread_type)
        
    if not response: return None
    client.type_message(*response)
    if total == 69:
        client.type_message("nice", thread_id, thread_type)
    return