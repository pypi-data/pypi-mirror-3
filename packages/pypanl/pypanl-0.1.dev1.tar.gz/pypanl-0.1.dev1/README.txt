README
======

Access Panl.com API -- Python version

Getting Started
---------------

To install the Panl API ...

  easy_install pypanl

Example Usage
---------------

Monitor a local RADIUS server by authenticating a test user

  import panl.utility
  import panl.custom
  ok = panl.utility.radius_auth('localhost', 'xyz123', 'fakeuser', 'abcd17')
  panl.custom.update(monitor_hash, monitor_key, 1, ok)

