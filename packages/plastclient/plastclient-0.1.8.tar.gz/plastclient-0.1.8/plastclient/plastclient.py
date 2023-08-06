## Plast client library
#

import oauth2, urllib, urllib2, urlparse, urlenc, json

class PlastClient(object):

    def __init__(self, host, key=None, secret=None, debug=False):
        self.host      = host
        self.key       = key
        self.secret    = secret
        self.State     = State(self)
        self.StateSet  = StateSet(self)
        self.Place     = Place(self)
        self.AccessKey = AccessKey(self)
        self.debug     = debug

    def call(self, req, oauth_sign=False):
        req['url'] = self.host+req['url']
        if req.has_key('params'):
            adder     = req['url'].find('?') >= 0 and '&' or '?'
            urlparams = urlenc.compose_qs(req['params'])
            req['url']  = '%s%s%s' % (req['url'],adder,urlparams)
        if oauth_sign:
            oauth_sign_request(req, self.key, self.secret)
        if self.debug:
            print req

        # Call the URL    
        resp = curl(req).body

        if self.debug:
            print resp
        return resp

class AccessKey(object):

    def __init__(self, pc):
        self.pc = pc

    def all(self):
        req = {
            'url'    : '/auth/accesskey',
            'method' : 'GET',
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def add(self):
        req = {
            'url'    : '/auth/accesskey',
            'method' : 'POST',
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def update(self, key, statesets=None, add=None, remove=None):
        data = {}
        if statesets != None:
            data['statesets'] = json.dumps(statesets)
        if add != None:
            data['add'] = json.dumps(add)
        if remove != None:
            data['remove'] = json.dumps(remove)
        req = {
            'url'    : '/auth/accesskey/%s/stateset' % key,
            'method' : 'PUT',
            'data'   : data
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def statesets(self, key, disabled=False):
        req = {
            'url'    : '/auth/accesskey/%s/stateset' % key,
            'method' : 'GET',
            'params' : {
                'disabled' : disabled
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def places(self, key, root=None):
        req = {
            'url'    : '/auth/accesskey/%s/place' % key,
            'method' : 'GET',
            'params' : {
                'root' : root
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))


class State(object):

    def __init__(self, pc):
        self.pc = pc

    def all(self):
        req = {
            'url'    : '/state',
            'method' : 'GET'
        }
        return json.loads(self.pc.call(req))

    def get(self, state_uuid):
        req = {
            'url'    : '/state/%s' % state_uuid,
            'method' : 'GET'
        }
        return json.loads(self.pc.call(req))

    def get_list(self, state_uuid_list):
        req = {
            'url'    : '/state',
            'method' : 'GET',
            'params' : {
                'uuids' : json.dumps(state_uuid_list)
            }
        }
        return json.loads(self.pc.call(req))

    def add(self, name, key):
        req = {
            'url'     : '/state',
            'method'  : 'POST',
            'data'    : {
                'name' : name
            },
            'headers'  : {
                'plast-accesskey' : key
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def update(self, state_uuid, key, name=None, description=None):
        data = {}
        if name != None:
            data['name'] = name
        if description != None:
            data['description'] = description
        print data
        req = {
            'url'     : '/state/%s' % state_uuid,
            'method'  : 'PUT',
            'data'    : data,
            'headers' : {
                'plast-accesskey' : key
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def search(self, query_text):
        req = {
            'url'     : '/state',
            'method'  : 'GET',
            'params'  : {
                'query_text' : query_text
            }
        }
        return json.loads(self.pc.call(req))

class StateSet(object):

    def __init__(self, pc):
        self.pc = pc

    def all(self):
        req = {
            'url'    : '/stateset',
            'method' : 'GET'
        }
        return json.loads(self.pc.call(req))

    def get(self, set_uuid):
        req = {
            'url'    : '/stateset/%s' % set_uuid,
            'method' : 'GET'
        }
        return json.loads(self.pc.call(req))

    def add(self, name, key):
        req = {
            'url'     : '/stateset',
            'method'  : 'POST',
            'data'    : {
                'name' : name
            },
            'headers'  : {
                'plast-accesskey' : key
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def update(self, set_uuid, key, name=None, description=None, states=None, disabled=None):
        data = {}
        if name != None:
            data['name'] = name
        if description != None:
            data['description'] = description
        if states != None:
            if type(states) != list:
                raise PlastError('/stateset/%s' % set_uuid, msg='states parameter of StateSet.update must be a list, now %s.' %  type(states), code=418)
            data['states'] = json.dumps(states)
        if disabled != None:
            data['disabled'] = disabled
        req = {
            'url'     : '/stateset/%s' % set_uuid,
            'method'  : 'PUT',
            'data'    : data,
            'headers' : {
                'plast-accesskey' : key
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def states(self, set_uuid, key=None):
        req = {
            'url'     : '/stateset/%s/states' % set_uuid,
            'method'  : 'GET',
            'headers'  : {
                'plast-accesskey' : key
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def search(self, query_text):
        req = {
            'url'     : '/stateset',
            'method'  : 'GET',
            'params'  : {
                'query_text' : query_text
            }
        }
        return json.loads(self.pc.call(req))

class Place(object):

    def __init__(self, pc):
        self.pc = pc

    def get(self, place_uuid):
        req = {
            'url'    : '/place/%s' % place_uuid,
            'method' : 'GET'
        }
        return json.loads(self.pc.call(req))

    def add(self, name, description, latitude, longitude, key, root=False):
        req = {
            'url'    : '/place',
            'method' : 'POST',
            'data'   : {
                'name'        : name,
                'description' : description,
                'latitude'    : latitude,
                'longitude'   : longitude,
                'root'        : root
            },
            'headers'  : {
                'plast-accesskey' : key
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def update(self, place_uuid, name, description, latitude, longitude, key):
        req = {
            'url'    : '/place/%s' % place_uuid,
            'method' : 'PUT',
            'data'   : {
                'name'        : name,
                'description' : description,
                'latitude'    : latitude,
                'longitude'   : longitude
            },
            'headers'  : {
                'plast-accesskey' : key
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))
        
    def modify_root(self, place_uuid, root, key):
        req = {
            'url'    : '/place/%s/root' % place_uuid,
            'method' : 'PUT',
            'data'   : {
                'root'  : root
            },
            'headers'  : {
                'plast-accesskey' : key
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

    def get_places(self, place_uuid):
        req = {
            'url'    : '/place/%s/places' % place_uuid,
            'method' : 'GET'
        }
        return json.loads(self.pc.call(req))

    def update_places(self, place_uuid, places_uuid_list, key):
        req = {
            'url'     : '/place/%s/places' % place_uuid,
            'method'  : 'PUT',
            'data'    : {
                'places' : json.dumps(places_uuid_list) 
            },
            'headers' : {
                'plast-accesskey' : key
            }
        }
        return json.loads(self.pc.call(req, oauth_sign=True))

class PlastError(Exception):
    def __init__(self, url, msg=None, code=None):
        self.url  = url
        self.msg  = msg
        self.code = code

    def __str__(self):
        return 'PlastError(%s) %s %s' % (self.code, self.url, self.msg)

def oauth_sign_request(req, key, secret):
    consumer = oauth2.Consumer(key, secret)
    client   = oauth2.Client(consumer)
    oreq = oauth2.Request.from_consumer_and_token(client.consumer, http_method=req['method'],http_url=req['url'])
    oreq.sign_request(client.method, client.consumer, client.token)
    req['url'] = oreq.to_url()

def curl(req):
    url     = req['url']
    method  = req['method']
    params  = req.has_key('params')  and req['params']  or {}
    data    = req.has_key('data')    and req['data']    or {}
    headers = req.has_key('headers') and req['headers'] or {}

    request = urllib2.Request(url)

    if req.has_key('headers'):
        for header in headers.keys():
            request.add_header(header, headers[header])
    if method != 'GET':
        request.get_method = lambda: req['method']
    try:
        if len(data) > 0:
            response = urllib2.urlopen(request, urllib.urlencode(data))
        else:
            response = urllib2.urlopen(request)
        response.body = response.read()
    except urllib2.HTTPError, e:
        response = e
        response.body = response.read()
        raise PlastError(url, msg=response.body, code=response.code)
    response.method = request.get_method()
    return response
