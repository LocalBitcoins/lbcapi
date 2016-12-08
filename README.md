HMAC example
============

```
from lbcapi import api

hmac_key = Your HMAC key here
hmac_secret = Your HMAC secret here

conn = api.hmac(hmac_key, hmac_secret)
conn.call('GET', '/api/myself/').json()
```
