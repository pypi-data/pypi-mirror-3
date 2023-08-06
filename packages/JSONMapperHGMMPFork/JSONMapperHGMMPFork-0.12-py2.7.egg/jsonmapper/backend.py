from httplib2 import Http
import simplejson
import logging
log = logging.getLogger(__name__)

class DBMessage(Exception):
    def __init__(self, message, returnobj):
        self.returnobj = returnobj
        self.message = message
    def __str__(self):
      return "<DBMessage: '{0}'>".format(self.message)
class DBException(Exception):pass

class Backend(object):
  def __init__(self, location):
    self.location = location
  
  def __call__(self, returnobj, **options):
    result = self.query(**options)
    return result[returnobj]

  def query(self, **options):
    h = Http()
    method = options.get("method", "GET")
    endpoint = "{}{}".format(self.location, options['url'])
    log.debug("Endpoint: %s, Method: %s", endpoint, method)
    if method == "POST":
      data = simplejson.dumps(options['data'])
      log.debug("DATA: %s", data)
      resp, content = h.request(endpoint, method=method, body = data, headers={'Content-Type': 'application/json'})
    else:
      resp, content = h.request(endpoint, method=method )
    log.debug("RESULT: %s", content[:5000])
    result = simplejson.loads(content)
    if result['status'] != 0: 
        raise DBException("Status: {status} Reason: {error_message}".format(**result))
    elif result.get('db_message'):
        raise DBMessage(result['db_message'], None)
    else: 
      return result
