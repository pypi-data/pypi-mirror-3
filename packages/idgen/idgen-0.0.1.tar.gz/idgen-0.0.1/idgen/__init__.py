''' 
Generates identifiers that:

   * match a desired format;
   * look random (if you activate crypto);
   * can be converted back to ints, given the password; and
   * use ALL possible values in the format

  enc = Encoder('aadd')
  enc.encode(123) -> 'ab23'
  enc.decode('ab23') -> 123

  enc = Encoder('vcv', types={'v': 'aeiou', 'c': 'qwrtpsdfg'})
  enc.encode(300) -> 'eda'

  enc = Encoder('adadad', password='jupiter')
  enc.encode(0) -> s9l6e8
  enc.encode(1) -> m8o4i5
  enc.decode('m8o4i5') -> 1
'''

from format import IntBox, Format, Digit
from string import ascii_lowercase
import hashlib

class Encoder(object):
  '''Converts between integers and strings of a specified format'''
  def __init__(self, fmt_string, types={}, password=None, hash_class=hashlib.sha256):
    '''fmt_string: The format of the strings to be encoded/decoded.
                   Each character represents one digit (position):

                   d: 0-9

                   a: a-z

       types:      An optional dict of format character to character
                   range; gets added to (and overrides) the default types;
                   character ranges may be strings or lists.

                   Example: types={'k': ['a', 'x', '9']}

       password:   An optional key for encrypting/decrypting strings; if not
                   provided, no crypto is used.
      '''

    default_types = {
        'd': '0123456789',
        'a': [chr(x) for x in range(ord('a'), ord('z')+1)],
    }
    types = dict(default_types.items() + types.items())
    digits = []
    for c in fmt_string:
      if c in types:
        digits.append(Digit(types[c]))
      else:
        digits.append(Digit([c])) # literal
    self.format = Format(digits)
    self.hash_class = hash_class
    self.password = password

  def _int_hash(self, input):
    h = self.hash_class(input)
    return int(h.hexdigest(), 16)

  def _crypt(self, dir):
    if not self.password:
      return
    digits = self.format.digits
    a = range(len(digits))
    if dir < 0:
      a.reverse()
    for i in a:
      d = [str(digits[j]) for j in a if j != i]
      if dir < 0:
        d.reverse()
      hash_input = self.password + ' '.join(d)
      hash_int = self._int_hash(hash_input)
      #print "hash_int=%s dir=%s" % (hash_int, dir)
      self.format.digits[i].encode(IntBox(hash_int), dir)

  def encode(self, n):
    '''Given an integer, encode it to a string'''
    self.format.encode(n)
    self._crypt(1)
    return str(self.format)

  def decode(self, s):
    '''Given a string, decode it to an integer'''
    self.format.decode(s)
    self._crypt(-1)
    return int(self.format)

