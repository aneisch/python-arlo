# coding: utf-8
# vim:sw=4:ts=4:et:
"""Base Python Class file for Netgear Arlo camera module."""
import os
import json
import requests

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


from pyarlo.const import (
        API_URL, DEFAULT_HEADERS, LOGIN_ENDPOINT, DEVICES_ENDPOINT, PARAMS)


class PyArlo(object):
    """Base object for Netgar Arlo camera."""


    def __init__(self, username=None, password=None, headers=DEFAULT_HEADERS):
        """Initialize the PyArlo object."""
        self.authenticated = None
        self.country_code = None
        self.date_created = None
        self.token = None
        self.userid = None

        # set username and password
        self.password = password
        self.username = username

        # initialize connection parameters
        self._headers = headers
        self._params = PARAMS
        self._params['email'] = self.username
        self._params['password'] = self.password
        self.session = requests.Session()

        # authenticate user
        self._authenticate()

    def __repr__(self):
        """Object representation."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.userid)

    def _authenticate(self):
        """Authenticate user and generate token."""
        url = API_URL + LOGIN_ENDPOINT
        data = self._query(url, method='POST')

        if isinstance(data, dict) and data.get('success'):
            self.authenticated = data.get('data').get('authenticated')
            self.country_code = data.get('data').get('countryCode')
            self.date_created = data.get('data').get('dateCreated')
            self.token = data.get('data').get('token')
            self.userid = data.get('data').get('userId')

            # update header with the generated token
            self._headers['Authorization'] = self.token

    def _query(self,
               url,
               method='GET',
               extra_params=None,
               extra_headers=None,
               raw=False):
        """Return a JSON object or raw session."""
        response = None

        # extend params
        if extra_params:
            params = self._params
            params.update(extra_params)
        else:
            params = self._params

        # extend headers
        if extra_headers:
            headers = self._headers
            headers.update(extra_headers)
        else:
            headers = self._headers

        if method == 'GET':
            req = self.session.get(url, headers=headers)
        elif method == 'PUT':
            req = self.session.put(url, json=params, headers=headers)
        elif method == 'POST':
            req = self.session.post(url, json=params, headers=headers)

        if req.status_code == 200:
            if raw:
                response = req
            else:
                response = req.json()
        return response


    #FIXME: needs to create an deviceType object to abstract methods
    @property
    def devices(self):
        """Return all devices on Arlo account."""
        devices = []
        url = API_URL + DEVICES_ENDPOINT
        data = self._query(url)

        for device in data.get('data'):
            devices.append(device.get('deviceName'))
        return devices