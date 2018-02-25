import re
from fbchat.models import ThreadType

#Class to keep state when checking if strings match regexes
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

#Maps ascii text to the full-width unicode variant
_WIDE_MAP = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
_WIDE_MAP[0x20] = 0x3000
    
def vaporwave(text):
    return text.translate(_WIDE_MAP)

#Nested dictionary setting from Bakuriu @ https://stackoverflow.com/questions/13687924
def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value
    
def get_name(client, author_id, thread_id, thread_type):
    user = client.fetchUserInfo(author_id)[author_id]
    
    #cache this, update on onNicknameChanged
    nicknames = {}
    nicknames[user.uid] = user.nickname
    if thread_type == ThreadType.GROUP:
        nicknames = client.fetchGroupInfo(thread_id)[thread_id].nicknames
        print(nicknames)
    
    
    nickname = nicknames.get(user.uid)
    
    
    name = "@"+(nickname or user.first_name)
    
    return name