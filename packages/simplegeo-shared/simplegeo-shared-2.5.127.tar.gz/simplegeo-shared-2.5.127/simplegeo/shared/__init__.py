from _version import __version__

API_VERSION = '1.0'

import copy, re
from decimal import Decimal as D

from httplib2 import Http
import oauth2 as oauth

import ipaddr

from urlparse import urljoin

from pyutil import jsonutil as json
from pyutil.assertutil import precondition, _assert

# example: http://api.simplegeo.com/1.0/feature/abcdefghijklmnopqrstuvwyz.json

def json_decode(jsonstr):
    try:
        return json.loads(jsonstr)
    except (ValueError, TypeError), le:
        raise DecodeError(jsonstr, le)

def swap(tupleab):
    return (tupleab[1], tupleab[0])

def deep_swap(struc):
    if is_numeric(struc[0]):
        _assert (len(struc) == 2, (type(struc), repr(struc)))
        _assert (is_numeric(struc[1]), (type(struc), repr(struc)))
        return swap(struc)
    return [deep_swap(sub) for sub in struc]

def deep_validate_lat_lon(struc, strict_lon_validation=False):
    """
    For the meaning of strict_lon_validation, please see the function
    is_valid_lon().
    """
    if not isinstance(struc, (list, tuple, set)):
        raise TypeError('argument is required to be a sequence (of sequences of...) numbers, not: %s :: %s' % (struc, type(struc)))
    if is_numeric(struc[0]):
        if not len(struc) == 2:
            raise TypeError("The leaf element of this structure is required to be a tuple of length 2 (to hold a lat and lon).")

        _assert_valid_lat(struc[0])
        _assert_valid_lon(struc[1], strict=strict_lon_validation)
    else:
        for sub in struc:
            deep_validate_lat_lon(sub, strict_lon_validation=strict_lon_validation)
    return True

SIMPLEGEOHANDLE_RSTR=r"""SG_[A-Za-z0-9]{22}(?:_-?[0-9]{1,3}(?:\.[0-9]+)?_-?[0-9]{1,3}(?:\.[0-9]+)?)?(?:@[0-9]+)?$"""
SIMPLEGEOHANDLE_R= re.compile(SIMPLEGEOHANDLE_RSTR)
def is_simplegeohandle(s):
    return isinstance(s, basestring) and SIMPLEGEOHANDLE_R.match(s)

FEATURES_URL_R=re.compile("http://(.*)/features/([A-Za-z_,-]*).json$")

def is_numeric(x):
    return isinstance(x, (int, long, float, D))

def is_valid_lat(x):
    return is_numeric(x) and (x <= 90) and (x >= -90)

def _assert_valid_lat(x):
    if not is_valid_lat(x):
        raise TypeError("not a valid lat: %s" % (x,))

def _assert_valid_lon(x, strict=False):
    if not is_valid_lon(x, strict=strict):
        raise TypeError("not a valid lon (strict=%s): %s" % (strict, x,))

def is_valid_lon(x, strict=False):
    """
    Longitude is technically defined as extending from -180 to
    180. However in practice people sometimes prefer to use longitudes
    which have "wrapped around" past 180. For example, if you are
    drawing a polygon around modern-day Russia almost all of it is in
    the Eastern Hemisphere, which means its longitudes are almost all
    positive numbers, but the easternmost part of it (Big Diomede
    Island) lies a few degrees east of the International Date Line,
    and it is sometimes more convenient to describe it as having
    longitude 190.9 instead of having longitude -169.1.

    If strict=True then is_valid_lon() requires a number to be in
    [-180..180] to be considered a valid longitude. If strict=False
    (the default) then it requires the number to be in [-360..360].
    """
    if strict:
        return is_numeric(x) and (x <= 180) and (x >= -180)
    else:
        return is_numeric(x) and (x <= 360) and (x >= -360)

def to_unicode(s):
    """ Convert to unicode, raise exception with instructive error
    message if s is not unicode, ascii, or utf-8. """
    if not isinstance(s, unicode):
        if not isinstance(s, str):
            raise TypeError('You are required to pass either unicode or string here, not: %r (%s)' % (type(s), s))
        try:
            s = s.decode('utf-8')
        except UnicodeDecodeError, le:
            raise TypeError('You are required to pass either a unicode object or a utf-8 string here. You passed a Python string object which contained non-utf-8: %r. The UnicodeDecodeError that resulted from attempting to interpret it as utf-8 was: %s' % (s, le,))
    return s

class Feature:
    def __init__(self, coordinates, geomtype='Point', simplegeohandle=None, properties=None, strict_lon_validation=False):
        """
        The simplegeohandle and the record_id are both optional -- you
        can have one or the other or both or neither.

        A simplegeohandle is globally unique and is assigned by the
        Places service. It is returned from the Places service in the
        response to a request to add a place to the Places database
        (the add_feature method).

        The simplegeohandle is passed in as an argument to the
        constructor, named "simplegeohandle", and is stored in the
        "id" attribute of the Feature instance.

        A record_id is scoped to your particular user account and is
        chosen by you. The only use for the record_id is in case you
        call add_feature and you have already previously added that
        feature to the database -- if there is already a feature from
        your user account with the same record_id then the Places
        service will return that feature to you, along with that
        feature's simplegeohandle, instead of making a second, duplicate
        feature.

        A record_id is passed in as a value in the properties dict
        named "record_id".

        geomtype is a GeoJSON geometry type such as "Point",
        "Polygon", or "Multipolygon". coordinates is a GeoJSON
        coordinates *except* that each lat/lon pair is written in
        order lat, lon instead of the GeoJSON order of lon, at.

        When a Feature is being submitted to the SimpleGeo Places
        database, if there is a key 'private' in the properties dict
        which is set to True, then the Feature is intended to be
        visible only to your user account. If there is no 'private'
        key or if there is a 'private' key which is set to False, then
        the Feature is intended to be merged into the publicly visible
        Places Database.

        Note that even if it is intended to be merged into the public
        Places Database the actual process of merging it into the
        public shared database may take some time, and the newly added
        Feature will be visible to your account right away even if it
        isn't (yet) visible to the public.

        For the meaning of strict_lon_validation, please see the
        function is_valid_lon().
        """
        try:
            deep_validate_lat_lon(coordinates, strict_lon_validation=strict_lon_validation)
        except TypeError, le:
            raise TypeError("The first argument, 'coordinates' is required to be a 2-element sequence of lon, lat for a point (or a more complicated set of coordinates for polygons or multipolygons), but it was %s :: %r. The error that was raised from validating this was: %s" % (type(coordinates), coordinates, le))

        if not (simplegeohandle is None or is_simplegeohandle(simplegeohandle)):
            raise TypeError("The third argument, 'simplegeohandle' is required to be None or to match this regex: %s, but it was %s :: %r" % (SIMPLEGEOHANDLE_RSTR, type(simplegeohandle), simplegeohandle))

        record_id = properties and properties.get('record_id') or None
        if not (record_id is None or isinstance(record_id, basestring)):
            raise TypeError("record_id is required to be None or a string, but it was: %r :: %s." % (type(record_id), record_id))
        self.strict_lon_validation = strict_lon_validation
        precondition(coordinates)
        self.id = simplegeohandle
        self.coordinates = coordinates
        self.geomtype = geomtype
        self.properties = {'private': False}
        if properties:
            self.properties.update(properties)

    @classmethod
    def from_dict(cls, data, strict_lon_validation=False):
        """
        data is a GeoJSON standard data structure, including that the
        coordinates are in GeoJSON order (lon, lat) instead of
        SimpleGeo order (lat, lon)
        """
        assert isinstance(data, dict), (type(data), repr(data))
        coordinates = deep_swap(data['geometry']['coordinates'])
        try:
            deep_validate_lat_lon(coordinates, strict_lon_validation=strict_lon_validation)
        except TypeError, le:
            raise TypeError("The 'coordinates' value is required to be a 2-element sequence of lon, lat for a point (or a more complicated set of coordinates for polygons or multipolygons), but it was %s :: %r. The error that was raised from validating this was: %s" % (type(coordinates), coordinates, le))
        feature = cls(
            simplegeohandle = data.get('id'),
            coordinates = coordinates,
            geomtype = data['geometry']['type'],
            properties = data.get('properties')
            )

        return feature

    def to_dict(self):
        """
        Returns a GeoJSON object, including having its coordinates in
        GeoJSON standad order (lon, lat) instead of SimpleGeo standard
        order (lat, lon).
        """
        return {
            'type': 'Feature',
            'id': self.id,
            'geometry': {
                'type': self.geomtype,
                'coordinates': deep_swap(self.coordinates)
            },
            'properties': copy.deepcopy(self.properties),
        }

    @classmethod
    def from_json(cls, jsonstr):
        return cls.from_dict(json_decode(jsonstr))

    def to_json(self):
        return json.dumps(self.to_dict())


class Client(object):
    realm = "http://api.simplegeo.com"
    endpoints = {
        'feature': 'features/%(simplegeohandle)s.json',
        'annotations': 'features/%(simplegeohandle)s/annotations.json',
    }

    def __init__(self, key, secret, api_version=API_VERSION, host="api.simplegeo.com", port=80):
        self.host = host
        self.port = port
        self.consumer = oauth.Consumer(key, secret)
        self.key = key
        self.secret = secret
        self.api_version = api_version
        self.signature = oauth.SignatureMethod_HMAC_SHA1()
        self.uri = "http://%s:%s" % (host, port)
        self.http = Http()
        self.headers = None

    def get_most_recent_http_headers(self):
        """ Intended for debugging -- return the most recent HTTP
        headers which were received from the server. """
        return self.headers

    def _endpoint(self, name, **kwargs):
        """Not used directly. Finds and formats the endpoints as needed for any type of request."""
        try:
            endpoint = self.endpoints[name]
        except KeyError:
            raise Exception('No endpoint named "%s"' % name)
        try:
            endpoint = endpoint % kwargs
        except KeyError, e:
            raise TypeError('Missing required argument "%s"' % (e.args[0],))
        return urljoin(urljoin(self.uri, self.api_version + '/'), endpoint)

    def get_feature(self, simplegeohandle):
        """Return the GeoJSON representation of a feature."""
        if not is_simplegeohandle(simplegeohandle):
            raise TypeError("simplegeohandle is required to match the regex %s, but it was %s :: %r" % (SIMPLEGEOHANDLE_RSTR, type(simplegeohandle), simplegeohandle))
        endpoint = self._endpoint('feature', simplegeohandle=simplegeohandle)
        return Feature.from_json(self._request(endpoint, 'GET')[1])

    def get_annotations(self, simplegeohandle):
        if not is_simplegeohandle(simplegeohandle):
            raise TypeError("simplegeohandle is required to match the regex %s, but it was %s :: %r" % (SIMPLEGEOHANDLE_RSTR, type(simplegeohandle), simplegeohandle))
        endpoint = self._endpoint('annotations', simplegeohandle=simplegeohandle)
        return json.loads(self._request(endpoint, 'GET')[1])

    def annotate(self, simplegeohandle, annotations, private):
        if not isinstance(annotations, dict):
            raise TypeError('annotations must be of type dict')
        if not len(annotations.keys()):
            raise ValueError('annotations dict is empty')
        for annotation_type in annotations.keys():
            if not len(annotations[annotation_type].keys()):
                raise ValueError('annotation type "%s" is empty' % annotation_type)
        if not isinstance(private, bool):
            raise TypeError('private must be of type bool')

        data = {'annotations': annotations,
                'private': private}

        endpoint = self._endpoint('annotations', simplegeohandle=simplegeohandle)
        return json.loads(self._request(endpoint,
                                        'POST',
                                        data=json.dumps(data))[1])

    def _request(self, endpoint, method, data=None):
        """
        Not used directly by code external to this lib. Performs the
        actual request against the API, including passing the
        credentials with oauth.  Returns a tuple of (headers as dict,
        body as string).
        """
        if data is not None:
            data = to_unicode(data)
        params = {}
        body = data
        request = oauth.Request.from_consumer_and_token(self.consumer,
            http_method=method, http_url=endpoint, parameters=params)

        request.sign_request(self.signature, self.consumer, None)
        headers = request.to_header(self.realm)
        headers['User-Agent'] = 'SimpleGeo Places Client v%s' % __version__

        self.headers, content = self.http.request(endpoint, method, body=body, headers=headers)

        if self.headers['status'][0] not in ('2', '3'):
            raise APIError(int(self.headers['status']), content, self.headers)

        return self.headers, content


class APIError(Exception):
    """Base exception for all API errors."""

    def __init__(self, code, msg, headers, description=''):
        self.code = code
        self.msg = msg
        self.headers = headers
        self.description = description

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s (#%s) %s" % (self.msg, self.code, self.description)

class DecodeError(APIError):
    """There was a problem decoding the API's response, which was
    supposed to be encoded in JSON, but which apparently wasn't."""

    def __init__(self, body, le):
        super(DecodeError, self).__init__(None, "Could not decode JSON from server.", None, repr(le))
        self.body = body

    def __repr__(self):
        return "%s content: %s" % (self.description, self.body)

def is_valid_ip(ip):
    try:
        ipaddr.IPAddress(ip)
    except ValueError:
        return False
    else:
        return True
