#!/usr/bin/python


import string
import unicodedata
filename = "@#$%i..â oé .\\/ss AB56"
uni = unicode(filename, encoding='utf-8',errors='replace')

#validFilenameChars = "-_.()%s%s" % (string.ascii_letters, string.digits)
#filename = filename.replace(' ','-')

#uni = "aaaa"
cleanedFilename = unicodedata.normalize('NFKD', uni).encode('ASCII', 'ignore')
#filename = "".join(c for c in cleanedFilename if c in validFilenameChars)
#filename = "".join(c for c in cleanedFilename )

print filename
print cleanedFilename

#print filename
