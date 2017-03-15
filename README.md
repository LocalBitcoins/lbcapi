lbcapi is a simple python wrapper for the Localbitocins API created to make it easier to make calls to our API and help you to develop applications that interface with LocalBitcoins.com.

To install
==========
The easiset way to install lbcapi is to use pip. Open up a terminal window and type the following command to install

    pip install lbcapi

If you're running OS X you will first need to install pip using homebrew.

If you're running Windows pip will come built-in with the latest version of Python.

Usage example (using HMAC)
============
This example uses the library to call the /api/myself/ endpoint

```
from lbcapi import api

hmac_key = Your HMAC key here
hmac_secret = Your HMAC secret here

conn = api.hmac(hmac_key, hmac_secret)
conn.call('GET', '/api/myself/').json()
```

To find out all the available API calls please see the API documentation on LocalBitcoins.com
https://localbitcoins.com/api-docs/