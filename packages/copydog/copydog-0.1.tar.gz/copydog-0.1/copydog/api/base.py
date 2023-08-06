# -*- coding: utf-8 -*-
import requests
from logging import getLogger
from dateutil.parser import parse
log = getLogger(__name__)


class ApiException(Exception):
    """ Error, raised by API wrapper """


class MissingProperty(ApiException):
    """ API object is missing property"""

    def __str__(self):
        return 'API object {0} is missing attribute "{1}"'.format(*self.args)

class ApiObject(object):
    date_fields = tuple()

    def __init__(self, client=None, **data):
        """ Abstract API object constructor.

        :param client: API client
        :param data: object internals
        """
        data = self.prepare_dates(data)
        self._data = data
        self.client = client
        self._uid = data.get('name', data.get('subject') or data.get('id'))
        self.validate()
        log.debug('Instantiated API object %s' % repr(self))

    def __getattr__(self, attr):
        try:
            return self._data[attr]
        except KeyError:
            raise MissingProperty(self, attr)

    def get(self, attr, default=None):
        return self._data.get(attr, default)

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'<{class_name} {identifier}>'.format(class_name=self.__class__.__name__, identifier=self._uid)

    def validate(self):
        """ Validate created object"""

    def prepare_dates(self, data):
        for field in self.date_fields:
            if data.get(field):
                data[field] = parse(data[field])
        return data


class ApiClient(object):
    """ Base class for all service APIs"""

    def default_payload(self):
        return {}

    def build_api_url(self, path):
        raise NotImplemented

    def get(self, path, **payload):
        return self.method('get', path, **payload)

    def post(self, path, data=None, **payload):
        return self.method('post', path, data, **payload)

    def put(self, path, data=None, **payload):
        return self.method('put', path, data, **payload)

    def method(self, method, path, data=None, headers=None, expect_json=True, **payload):
        payload.update(self.default_payload())
        response = requests.request(method=method, url=self.build_api_url(path),
                                    headers=headers, data=data, params=payload)
        log.debug('Request: [%s] %s', response.request.method, response.request.full_url)
        log.debug('Request data: %s', response.request.data)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            log.error('Request failed: %s', e.response.content)
            raise e

        if response.json is not None:
            return response.json
        else:
            if expect_json:
                raise ApiException('JSON expected, got %s' % response.content)
            return True

