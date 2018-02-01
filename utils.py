import re

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