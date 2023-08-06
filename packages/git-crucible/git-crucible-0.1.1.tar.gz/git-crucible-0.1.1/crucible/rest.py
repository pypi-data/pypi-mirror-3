import urllib2
import base64


def request(url, method, body=None, username=None, password=None):
    headers={'Content-Type': 'application/xml',
             "Accept": 'application/xml'}
    if username:
        headers["Authorization"] = 'Basic %s' % base64.encodestring("%s:%s" % (username, password))[:-1]

    req = urllib2.Request(url=url, data=body, headers=headers)
    return urllib2.urlopen(req)
