import requests
import json

with open("conf.json", "r") as f:
    config = json.load(f)
    
url = "https://api.datamuse.com/words"

def get_synonyms(word):
    r = requests.get(url, params =
    {
        "ml" : word,
        "topics" : "masculine",
        "md" : "f",
    })
    
    words = r.json()
    
    return [word["word"] for word in words[0:10]]
    
def get_frequency(data):
    tags = data["tags"]
    for string in tags:
        if string.startswith("f:"):
            return float(string.split(":")[1])
           
    
def chadlier(word):
    synonyms = get_synonyms(word)
    
    #synonyms.sort(key = get_frequency)
    
    weirdest = synonyms[0:10]
    
    return weirdest