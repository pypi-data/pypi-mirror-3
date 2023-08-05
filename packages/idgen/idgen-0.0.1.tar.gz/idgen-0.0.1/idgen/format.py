'''
Private classes to support transcoder.
'''
from string import ascii_lowercase
import hashlib

class IntBox(object):
  '''A hack to pass an int by reference'''
  def __init__(self, i):
    self.i = i

class Digit(object):
  '''Private - A digit or character within a format'''
  def __init__(self, chars, val=0):
    '''chars: list or string of characters this digit can use;
              its length becomes the digit's base
       val:   optional integer setting initial value of digit
    '''
    self.chars = list(chars)
    self.base = len(chars)
    self.v = val # int

  def reset(self):
    self.v = 0

  # consume and destroy part of intbox to set my state:
  def encode(self, intbox, dir=1):
    self.v = (self.v + dir * intbox.i % self.base) % self.base
    intbox.i = int(intbox.i/self.base)

  def to_intbox(self, intbox):
    intbox.i *= self.base
    intbox.i += self.v
    
  # consume and destroy part of char_list to set my state:
  def decode(self, char_list):
    c = char_list.pop()
    self.v = self.chars.index(c)

  def __str__(self):
    return self.chars[self.v]

  def __int__(self):
    return self.v

class Format(object):
  '''Private - A set of Digits and literals, each of which can have different chars'''
  def __init__(self, digits):
    self.digits = digits

  # int -> str
  def encode(self, i):
    box = IntBox(i)
    for d in reversed(self.digits): # start w least
      d.reset()
      d.encode(box)
    return ''.join([str(d) for d in self.digits])

  # str -> int
  def decode(self, s):
    cl = list(s)
    for d in reversed(self.digits): # start w least
      d.decode(cl)
    box = IntBox(0)
    for d in self.digits:
      d.to_intbox(box)
    return box.i
      
  def __str__(self):
    return ''.join([str(d) for d in self.digits])

  def __int__(self):
    box = IntBox(0)
    for d in self.digits:
      d.to_intbox(box)
    return box.i
