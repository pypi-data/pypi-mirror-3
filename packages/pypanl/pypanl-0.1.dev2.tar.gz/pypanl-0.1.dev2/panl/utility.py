#!/usr/bin/env python
# vim: se expandtab sw=4 ai:

"""
Useful utility and support functions
"""

class Error(Exception):
    """Base of all exceptions."""
    pass

def credentials(app='pypanl', cf='~/pypanl.cf'):
    """ set and maintain Panl user credentials in the system keyring. """
    import getpass, keyring, ConfigParser
    from os.path import expanduser
    cf = expanduser(cf)
    config = ConfigParser.SafeConfigParser({'username': ''})
    config.read(cf)
    if not config.has_section('auth'):
        config.add_section('auth')
    uname = config.get('auth', 'username')
    pwd = None
    if uname:
        pwd = keyring.get_password(app, uname)
    if not pwd:
        uname = raw_input('Username hash: ')
        config.set('auth', 'username', uname)
        config.write(open(cf, 'w'))
        pwd = getpass.getpass('Password: ')
        keyring.set_password(app, uname, pwd)
    return uname, pwd

# Example:
#  ok = panl.utility.radius_auth(radius_server, secret, radius_user, password)
#  panl.custom.update(monitor_hash, monitor_key, 1, ok)

def radius_auth(server, secret, user, password, nas_id='localhost'):
    """ authorize user via radius server """
    import pyrad.packet
    from pyrad.client import Client
    from pyrad.dictionary import Dictionary
    from StringIO import StringIO
    import socket, sys

    # don't need the whole RADIUS dictionary file for this trivial use
    dfile = StringIO('''
        ATTRIBUTE       User-Name               1       string
        ATTRIBUTE       User-Password           2       string
        ATTRIBUTE       NAS-Identifier          32      string
        ''')

    srv = Client(server=server, secret=secret, dict=Dictionary(dfile))
    req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest,
                  User_Name=user, NAS_Identifier=nas_id)
    req["User-Password"] = req.PwCrypt(password)
    try:
        reply = srv.SendPacket(req)
    except pyrad.client.Timeout:
        return False
    except socket.error, error:
        return False
    return reply.code == pyrad.packet.AccessAccept


