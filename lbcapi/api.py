import hashlib
import hmac as hmac_lib

import requests
import time

import sys


def oauth2(access_token, client_id, client_secret=None, refresh_token=None, server='https://localbitcoins.com'):
    conn = Connection()
    conn._set_oauth2(server, client_id, client_secret, access_token, refresh_token)
    return conn


def hmac(hmac_key, hmac_secret, server='https://localbitcoins.com'):
    conn = Connection()
    conn._set_hmac(server, hmac_key, hmac_secret)
    return conn


class Connection():

    def __init__(self):
        self.server = None

        # OAuth2 stuff
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.refresh_token = None
        self.expiry_seconds = None

        # HMAC stuff
        self.hmac_key = None
        self.hmac_secret = None

    def call(self, method, url, params=None, stream=False, files=None):
        # Direct params={} in method signature is errorneus.
        if params is None:
            params = {}

        method = method.upper()
        if method not in ['GET', 'POST']:
            raise Exception(u'Invalid method {}!'.format(method))

        if method == 'GET' and files:
            raise Exception(u'You cannot send files with GET method!')

        # If URL is absolute, then convert it
        if url.startswith(self.server):
            url = url[len(self.server):]

        if sys.version_info <= (3, 0):
            # If not py3 - convert parameters into list of tuples.
            # This makes request encoding to keep the order.
            # In py3 "requests" lib fails with list of tuples,
            # so the dict is necessary.
            params = params.items()



        # If OAuth2
        if self.access_token:

            # Refresh session, if possible
            if self.refresh_token and self.client_id and self.client_secret:
                refresh_params = {
                    'refresh_token': self.refresh_token,
                    'grant_type': 'refresh_token',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                }
                r = requests.post(self.server + '/oauth2/access_token/', data=refresh_params)
                self.access_token = r.json()['access_token']
                self.refresh_token = r.json()['refresh_token']
                self.expiry_seconds = int(r.json()['expires_in'])

            headers = {
                'Authorization-Extra': 'Bearer ' + self.access_token,
            }

            if method == 'GET':
                return requests.get(self.server + url, params=params, headers=headers, stream=stream)
            else:
                return requests.post(self.server + url, data=params, headers=headers, stream=stream, files=files)

        # If HMAC
        elif self.hmac_key:

            # Loop, so retrying is possible if nonce fails
            while True:

                if sys.version_info >= (3, 0):
                    # There is no "long" type in py3
                    nonce = int(time.time()) * 10**3

                else:
                    nonce = long(time.time() * 1000)

                # POST method. Kind of tricky because of files
                if method == 'POST':

                    # Prepare request, but do not send it yet
                    api_request = requests.Request('POST', self.server + url, data=params, files=files).prepare()

                    # Calculate signature
                    message = str(nonce) + str(self.hmac_key) + str(url)
                    if api_request.body:
                        message += str(api_request.body)

                    if sys.version_info >= (3, 0):
                        signature = hmac_lib.new(
                            bytes(self.hmac_secret, 'utf-8'),
                            msg=bytes(message, 'utf-8'),
                            digestmod=hashlib.sha256).hexdigest().upper()

                    else:
                        signature = hmac_lib.new(
                            str(self.hmac_secret),
                            msg=str(message),
                            digestmod=hashlib.sha256).hexdigest().upper()

                    # Store signature and other stuff to headers
                    api_request.headers['Apiauth-Key'] = self.hmac_key
                    api_request.headers['Apiauth-Nonce'] = str(nonce)
                    api_request.headers['Apiauth-Signature'] = signature

                    # Send request
                    session = requests.Session()
                    response = session.send(api_request, stream=stream)

                # GET method
                else:

                    params_urlencoded = requests.models.RequestEncodingMixin._encode_params(params)
                    message = str(nonce) + self.hmac_key + url + params_urlencoded
                    
                    if sys.version_info >= (3, 0):
                        signature = hmac_lib.new(
                            bytes(self.hmac_secret, 'utf-8'), 
                            msg=bytes(message, 'utf-8'), 
                            digestmod=hashlib.sha256).hexdigest().upper()
                    else:
                        signature = hmac_lib.new(
                            str(self.hmac_secret), 
                            msg=str(message), 
                            digestmod=hashlib.sha256).hexdigest().upper()

                            
                    headers = {
                        "Apiauth-Key": self.hmac_key,
                        "Apiauth-Nonce": str(nonce),
                        "Apiauth-Signature": signature,
                    }

                    response = requests.get(self.server + url, params=params, headers=headers, stream=stream)

                # If HMAC Nonce is already used, then wait a little and try again
                try:
                    response_json = response.json()
                    if response_json.get('error', {}).get('error_code') == '42':
                        time.sleep(0.1)
                        continue
                except:
                    # No JSONic response, or interrupt, better just give up
                    pass

                return response

        raise Exception(u'No OAuth2 or HMAC connection initialized!')

    def get_access_token(self):
        return self.access_token

    def get_refresh_token(self):
        return self.refresh_token

    def get_expiry_seconds(self):
        return self.expiry_seconds

    def _set_oauth2(self, server, client_id, client_secret, access_token, refresh_token):
        self.server = server
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry_seconds = None
        self.hmac_key = None
        self.hmac_secret = None

    def _set_hmac(self, server, hmac_key, hmac_secret):
        self.server = server
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.refresh_token = None
        self.expiry_seconds = None
        self.hmac_key = hmac_key
        self.hmac_secret = hmac_secret
