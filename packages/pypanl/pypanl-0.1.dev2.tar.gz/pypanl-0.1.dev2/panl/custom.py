#!/usr/bin/env python
# vim: se expandtab sw=4 ai:

# Example:
#  update(monitor_hash, monitor_key, 1, True)

def update(monitor, secret, value=0, up=True, note=None):
    from urllib2 import urlopen, Request
    try: import json
    except ImportError: import simplejson as json

    # XXX test that value is int or float
    url = 'https://api.panl.com/%s?k=%s&value=%d&up=%s' \
            % (monitor, secret, value, '1' if up is True else '0')
    #if note:
    #    url = url + '&note=%s' % urlencode(note)
    req = Request(url, None, {'Content-Type': 'application/json'})
    try:
        resp = urlopen(req)
    except URLError:
        import sys
        print 'update error: %s' % str(sys.exc_info()[1])
        return
    try:
        status = json.load(resp)
        if status.get('success') != 'True':
            print 'Panl update failed.'
    except ValueError:
        print 'unexpected result returned'

