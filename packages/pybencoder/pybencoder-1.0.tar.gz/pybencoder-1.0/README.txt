PyBencoder - your bencoded strings module
--------------------------------------------

What is a Bencoded String?
===========================

Bencode (pronounced like B encode) is the encoding used by the peer-to-peer file sharing system BitTorrent
for storing and transmitting loosely structured data.

For more info on bencoding check out http://en.wikipedia.org/wiki/Bencode/.

It provides:
 - decoding of the different bencoded elements
 - encoding of the allowed types (byte strings, integers, lists, and dictionaries).


Requirements
===========================

Requires Python 2.6 or later.


Installation
===========================


Usage
===========================

Import the module
------------------

from bencoder import PyBencoder


Encoding
---------

Encoding is very easy to do. Just pass as an argument your data to encode method.
It will automagically call the right encoder for you.

ben = PyBencoder()

ben.encode(123)         # encode an integer 'i123e'
ben.encode('123')       # encode a string '3:123'
ben.encode([1, 2, 3])   # encode a list 'li1ei2ei3ee'
ben.encode([1, 2, [ 4, 5]])  # encode a slightly more complex list 'li1ei2eli4ei5eee'
ben.encode({ 'one': 1, 'two': 2, 'three': 3 })   # encode a dictionary 'd5:threei3e3:twoi2e3:onei1ee'


Decoding
---------

Decoding is also easy to deal with. Just pass the bencoded string to decode method.
Two mentions:
- the first char of your bencoded string must be actually bencoded data, no garbage is allowed
- at the end of the bencoded string it might be garbage data; after the extraction, you can also retrieve it

ben = PyBencoder()

ben.decode('i123e')     # decode an integer 123
ben.decode('i123esomeothergarbagedata') # decode an integer with garbage data at the end
ben.get_left()          # gets what's left -> 'someothergarbagedata'

ben.decode('3:123somegarbage')     # decode a 3 chars string

ben.decode('li1ei2eli4ei5eee')     # decode a list [1, 2, [4, 5]]
