#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Kemvi: Python client library

Provides programmatic access to Kemvi's semantic search engine for 
computable data.

Sign up for API access at http://www.kemvi.com.
Then, set kemvi.API_KEY to get started.

Sample usage::

    import kemvi
    kemvi.entity('massachusetts')[0].property('unemployment rate')[0].value()

This will return a time series of Massachusetts unemployment rate.

Copyright (c) 2011 `Kemvi, Inc. <http://kemvi.com>`_.  All rights reserved.

email: info@kemvi.com

The kemvi package is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 3.0 of the License, or (at your option) any later version.

This package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this package; if not, see 
http://www.gnu.org/licenses/gpl-3.0.txt    
"""

__author__ = 'Kemvi (info@kemvi.com)'
__copyright__ = 'Copyright (c) 2011 Kemvi'
__license__ = 'GPL'
__version__ = '0.1.0'
__api_version__ = 1

import sys
import urllib
import urllib2
try: import simplejson as json
except ImportError: import json
# Handle Unicode:
#sys.setdefaultencoding('utf-8')

BASE_URL = "http://www.kemvi.com/api/"
MAX_CALL = 300
API_KEY = None

class KemviError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "KemviError: " + repr(self.value)

def __test__():
    """
    Test Kemvi API file. Currently unimplemented.

    No arguments.
    No return value.
    
    """
    pass

def __server_call__(params):
    """
    Transmit an API call to Kemvi servers.

    Arguments:
    ----------
    params -- dictionary of API arguments and values. Variable-length.

    Returns:
    --------
    Return value varies based on the type of call.

    """
    params['api_version'] = __api_version__
    post = json.dumps(params)
    req = urllib2.Request(BASE_URL, post)
    try:
        server_json = urllib2.urlopen(req).read()
    except urllib2.HTTPError:
        raise KemviError("Oops. Something went wrong on the server. " +
            "Please contact support@kemvi.com to let us know!")
    server_data = json.loads(server_json)
    if not server_data['success']:
        raise KemviError(server_data['error'])
    response = server_data['response']
    return response

def __ping__():
    """
    Ping Kemvi servers to check if this API library is up to date.

    Takes no arguments.
    Returns None.
    """
    global MAX_CALL
    params = {'key': API_KEY, 'type':'ping', 'version':__version__}
    response = __server_call__(params)
    MAX_CALL = response['max_call']

def __test__():
    assert True
    pass

class Property:
    
    """
    Represents a single property for a single entity.

    Arguments:
    ----------
    _id -- string; internal identifier for a property
    units -- string; the units of measure for the property
    source -- string; the source of this specific property
    name -- string; human-readable property label
    entity_id -- string; identifier of entity to which this *Property* 
        instance is attached.  Used to get a value for this entity-property
        pair

    """
    
    def __init__(self, _id, units, source, name, entity_id):
        self._id = _id
        self.units = units
        self.source = source
        self.name = name
        self.entity_id = entity_id

    def __repr__(self):
        return "Property(" + self.name + ")"

    def value(self):
        """
        Get the value for this property for the entity to which it's attached.

        Takes no arguments.

        Returns:
        --------
        Varies based on the type of data requested:
        For time series data, wo lists are returned, one of times, the other of
            values.
        If the requested value is an entity, e.g. the country that contains a
            state, the returned value is another *Entity* object

        """
        params = {'key': API_KEY, 'type':'value', 'property_id':self._id, 
            'entity_id':self.entity_id}
        response = __server_call__(params)
        if response['datatype'] == 'entity':
            return [Entity(**e) for e in response['value']]
        elif response['datatype'] == 'timeseries':
            return response['times'], response['value']
        else:
            return response['value']

class Entity:

    """
    Represents a single property for a single entity.

    Arguments:
    ----------
    _id -- string; internal identifier for a property
    units -- string; the units of measure for the property
    source -- string; the source of this specific property
    name -- string; human-readable property label
    entity_id -- string; identifier of entity to which this *Property* 
        instance is attached.  Used to get a value for this entity-property
        pair

    """
    
    def __init__(self, _id, type, name):
        self._id = _id
        self.type = type
        self.name = name

    def property(self, property=None, show=False):
        params = {'key': API_KEY, 'type':'property', 'id':self._id, 'q':property}
        response = __server_call__(params)
        ret = []
        for item in response:
            item['entity_id'] = self._id
            ret.append(Property(**item))
        if show:
            i = 0
            for val in ret:
                print i, val.name
                i += 1
        return ret

    def __repr__(self):
        n = self.name
        if len(n) > 30:
            n = n[:27] + "..."
        return "Entity(" + self.type + ": " + n + ")"

    def __cmp__(self, other):
        return cmp(self.name, other.name)

def entity(query):
    """
    Search for an entity.

    Arguments:
    ----------
    query: a search term, as a string.

    Returns:
    --------
    List of Entity objects that matched the search.

    """
    params = {'key': API_KEY, 'type':'entity', 'q':query}
    response = __server_call__(params)
    ret = []
    for item in response:
        ret.append(Entity(**item))
    return ret

def matrix(entities, properties):
    """
    Build a matrix of values for specific properties of specified entities.

    Arguments:
    ----------
    entities: list of Entity objects
    properties: list of Property objects. Ideally, these Property objects
        are properties of many or all of the Entity objects in entities.

    Returns:
    --------
    List of lists.  Each sub-list is a row of the matrix, and represents an
        entity.  The value in each sub-list (row) with index i represents the
        property with index i in the properties argument.
        
        When the property requested is a time series, only the most recent value
        is returned.

    """
    entity_ids = json.dumps([e._id for e in entities])
    property_ids = json.dumps([p._id for p in properties])
    num = len(entities) * len(properties)
    print "Requesting", num, "values..."
    params = {'key': API_KEY, 'type': 'matrix', 
        'entities': entity_ids,
        'properties': property_ids}
    response = __server_call__(params)
    return response['matrix']

if not API_KEY:
    print "No API key is defined. Please set kemvi.API_KEY = 'your-api-key'"
else:
    __ping__()


if __name__ == "__main__":
    __test__()

