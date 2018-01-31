#Thesaurus service provided by words.bighugelabs.com

import requests
import json

with open("conf.json", "r") as f:
    config = json.load(f)

url = "https://words.bighugelabs.com/api/{version}/{api_key}/{word}/{format}"
API_VERSION = 2
API_KEY = config["thesaurus"]["API_KEY"]
API_FORMAT = ""

def get_synonyms(word):
    r = requests.get(url.format(version=API_VERSION,
                                api_key=API_KEY,
                                word=word,
                                format=API_FORMAT))
    return parse_response(r)
    
def parse_response(r):    
    if r.status_code == 200:
        #print(r.text)
        return [word.split("|")[2] for word in r.text.strip().split("\n")]
    elif r.status_code == 303:
        return parse_response(requests.get(r.headers["Location"]))
    else:
        return []
