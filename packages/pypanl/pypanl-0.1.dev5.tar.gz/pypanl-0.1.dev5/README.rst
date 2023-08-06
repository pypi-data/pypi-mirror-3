README
======

Access the Panl.com API -- Python version

Getting Started
---------------

If you have setuptools installed, to install the Panl API, type::

  easy_install pypanl

Otherwise, unpack the distribution zipped tar-file, change directory to the
newly created folder and type::

  python setup.py install

For Windows, type::

  setup.py install


Create a Panl Monitor
---------------------

1. Visit http://panl.com/ to create an account. On the Monitors page,
   click +New Monitor.

2. Configure the new monitor as follows:

   * Mode: on [the default]

   * Type -> Custom

   * Name: *something mnemonic here, e.g. a server hostname*

   * Error Action: Alert

   * Expected Time: Every 15 minutes

   * Overdue Action: Alert

   * on the Contacts tab tick Alerts for the appropriate device
     (email, SMS, etc.) and optionally add an SMS device if you need
     an immediate push alert, otherwise email will be okay

3. Save

4. click on the new monitor's name (i.e. *something mnemonic*),
   scroll down and note the second line under the API Calls. It will
   look like this::

     https://api.panl.com/aWfBto?up=Yes&value=23&k=6776cd9166e2c9a545e258a7e725f64e

   You need to grab the Hash Code and the Access Key from this.
   The "Hash Code" is the six-character string (also provided on the
   Edit Monitor page), and the "Access Key" is the longer hex string.


Example Usage
---------------

Monitor a local RADIUS server by authenticating a test user::

  monitor_hash = 'aWfBto'
  monitor_key = '6776cd9166e2c9a545e258a7e725f64e'

  import panl.custom, panl.utility

  ok = panl.utility.radius_auth('localhost', 'xyz123', 'fakeuser', 'abcd17')
  panl.custom.update(monitor_hash, monitor_key, 1, ok)

