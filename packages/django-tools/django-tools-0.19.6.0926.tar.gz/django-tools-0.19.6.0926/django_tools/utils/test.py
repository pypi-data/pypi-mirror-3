# coding: utf-8

import urllib2

req = urllib2.Request("http://www.python.org")
opener = urllib2.build_opener()
#opener.addheaders = [("Referer", "/")]
response = opener.open(req, None)

#print response.read()
#print response.info()

print req.headers
print req.unredirected_hdrs
