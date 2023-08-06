#!/usr/bin/env python
# vim: se expandtab sw=4 ai:

"""Useful utility and support functions."""

class Error(Exception):
    """Base of all exceptions."""
    pass

def credentials(app='pypanl', cf='~/pypanl.cf'):
    """set and maintain Panl user credentials in the system keyring."""
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

"""probes -- test hosts for specific services"""

def port_probe_interact(host, port, expect=None, timeout=15, tls=False, udp=False, certreqd=False):
    """probe target host for a listening port; return active Telnet object
       for further interaction.

    A generic probe for an open (listening) port with optional test for
    initial response string.

    - returns (<telnetlib.Telnet object>, response_string) on success;
      or (None, explanation_string) if open failed.
    - timeout is in seconds
    - if expect is a string, must see that before timeout for success
    - if expect is '', then like None but may return a really fast response
    - now completely binary safe due to using a hacked telnetlib.
    - set tls=True to negotiate a TLS/SSL connection
    """
    from telnetlib_panl import Telnet
    import socket

    # XXX Telnet.open() raises socket.error for any DNS issues.
    #     we should test DNS ourselves first to disambiguate.

    tn = Telnet()
    try:
        try:
            resp = ''
            tn.open(host, port, timeout, tls, certreqd, udp)
            if expect is None:
                # just test that the socket is open; response will be ignored
                resp = tn.read_very_lazy()
            elif expect is '':
                # read whatever prompt may have arrived, without blocking
                resp = tn.read_very_eager()
            else:
                # read (block) until we see the expect string or timeout
                matched = tn.read_until(expect, timeout)
                # tack on the probable rest of the prompt to the response
                resp = matched + tn.read_lazy()
        except socket.timeout:
            # might be a server here, but took too long to reply
            return None, 'connection timed out'
        except socket.error:
            # no host, port not open
            return None, 'no service'
        except EOFError:
            return None, 'connection is closed'
    except:
        # any other error, assume the worst but explain
        import sys
        return None, str(sys.exc_info()[1])     # sys.exc_info()[0].__name__

    if not expect:
        return tn, '' if expect is None else resp
    elif matched.endswith(expect):
        return tn, resp
    elif not resp:
        return None, 'no response received'
    else:
        return None, 'unexpected response: %s' % resp

def port_probe(host, port, **opts):
    """generic probe for an open (listening) port with optional test for
       initial response string.

    - returns (True|False, explanation_string)
    - takes port_probe_interact()'s args
    - if expect is a string, must see that before timeout for success
    - if expect is '', then like None but may return a really fast response

    Eg:
      test for an SSH server and return the response banner, whatever it is.
        ret, resp = port_probe('localhost', 22, '\n')
      test for an SSH server and expect to see 'SSH' in the response banner.
        ret, resp = port_probe('localhost', 22, 'SSH')
    """
    tn, expl = port_probe_interact(host, port, **opts)
    if tn is None:
        return False, expl
    else:
        try: tn.close()
        except: pass
        return True, expl

"""protocol probes for some popular, well-known services"""

def mssql_probe(host, port=1433, timeout=15):
    """probe target host for an MS SQL server
    
    XXX very stupid implementation: just tests for an open and listening port.
    - timeout is in seconds
    """
    return port_probe(host, port, timeout=timeout)

def telnet_probe(host, port=23, timeout=15, tls=False, certreqd=False):
    """probe target host for a telnet service.

    - non-auth implementation: just tests for an open and listening port,
      and watches for an initial IAC option negotiation sequence.
    XXX note that there's no standard behaviour from a telnet server.
      we may encounter one that doesn't initiate an option negotiation.
    - timeout is in seconds
    """
    return port_probe(host, port, expect='\377', timeout=timeout, tls=tls,
                        certreqd=certreqd)

def telnets_probe(host, port=992, timeout=15, certreqd=False):
    """probe target host for a telnet TLS/SSL service. See telnet_probe()"""
    return telnet_probe(host, port, timeout=timeout, tls=True, certreqd=certreqd)

def ftp_probe(host, port=21, timeout=15):
    """probe target host for an ftp service

    - non-auth implementation: just tests for an open and listening port,
      and watches for an initial "service available" response.
    - timeout is in seconds
    """
    # XXX should we send a QUIT command before closing conn to avoid
    #  cluttering host's error logs?
    return port_probe(host, port, expect='220 ', timeout=timeout)

def imap_probe(host, port=143, timeout=15, tls=False, certreqd=False):
    """probe target host for an imap4 service

    - non-auth implementation: just tests for an open and listening port,
      and watches for an initial "service available" response.
    - timeout is in seconds
    """
    return port_probe(host, port, expect='* OK', timeout=timeout, tls=tls,
                        certreqd=certreqd)

def imaps_probe(host, port=993, timeout=15, certreqd=False):
    """probe target host for an imap4 SSL service"""
    return imap_probe(host, port, timeout=timeout, tls=True, certreqd=certreqd)

def pop3_probe(host, port=110, timeout=15, tls=False, certreqd=False):
    """probe target host for a pop3 service.

    - non-auth implementation: just tests for an open and listening port,
      and watches for an initial "service available" response.
    - timeout is in seconds
    """
    return port_probe(host, port, expect='+OK', timeout=timeout, tls=tls,
                        certreqd=certreqd)

def pop3s_probe(host, port=995, timeout=15, certreqd=False):
    """probe target host for a pop3 SSL service"""
    return pop3_probe(host, port, timeout=timeout, tls=True, certreqd=certreqd)

def ssh_probe(host, port=22, timeout=15, expect='SSH-'):
    """probe target host for a ssh v2.0 service.

    - non-auth implementation: just tests for an open and listening port,
      and watches for an initial "service available" response.
    - timeout is in seconds
    """
    return port_probe(host, port, expect=expect, timeout=timeout)

def radius_auth(server, secret, user, password, nas_id='localhost'):
    """authorize user via radius server.

    Example:
     ok = panl.utility.radius_auth(radius_server, secret, radius_user, password)
     panl.custom.update(monitor_hash, monitor_key, 1, ok)
    """
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

