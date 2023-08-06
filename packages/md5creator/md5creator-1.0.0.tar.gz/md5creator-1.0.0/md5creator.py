#!/usr/bin/python
#md5creator by Dr@G
#-----------------------------------------------
import hashlib
#-----------------------------------------------
text=raw_input('String to create md5 hash:~# ')
hash=hashlib.md5(text).hexdigest()
#-----------------------------------------------
print hash

