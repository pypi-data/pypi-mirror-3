from httplib2 import Http
import simplejson
import logging
log = logging.getLogger(__name__)

class DBMessage(Exception):
    def __init__(self, message, result_key):
        self.result_key = result_key
        self.message = message
    def __str__(self):
      return "<DBMessage: '{0}'>".format(self.message)
class DBException(Exception):pass

class RemoteProc(object):
  def __init__(self, remote_path, method, root_key, result_cls):
    self.remote_path = remote_path
    self.method      = method
    self.root_key    = root_key
    self.result_cls  = result_cls  
  def __call__(self, backend, data):
    return self.result_cls.wrap(backend(self.root_key, url=self.remote_path, method=self.method, data=data))


class Backend(object):
  def __init__(self, location):
    self.location = location
  
  def __call__(self, result_key, **options):
    result = self.query(**options)
    return result[result_key]

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
        raise DBException("Status: {status} Reason: {errorMessage}".format(**result))
    elif result.get('db_message'):
        raise DBMessage(result['dbMessage'], None)
    else: 
      return result
