from formencode.variabledecode import variable_decode
from formencode.validators import Invalid
from pyramid.httpexceptions import HTTPNotImplemented, HTTPUnauthorized
from pyramid.view import view_config

import logging
log = logging.getLogger(__name__)

class BaseHandler(object):
  def __init__(self, context, request):
      self.request = request
      self.context = context

class FullValidatedFormHandler(object):
  def __init__(self, context = None, request = None):
      self.request = request
      self.context = context
      self.result = {'values':{}, 'errors':{}, 'schemas' : self.schemas}
      ### generate groups error/value groups for each schema
      self.result['values'].update([(k,{}) for k in self.schemas.keys()])
      self.result['errors'].update([(k,{}) for k in self.schemas.keys()])


  @view_config(request_method='GET')
  def GET(self):
    self.request.session.new_csrf_token()
    return self.result
  @view_config(request_method='POST')
  def POST(self):
    req = self.request
    if req.params['token'] != req.session.get_csrf_token():
      raise HTTPUnauthorized("CSRF Token missing or wrong.")
    return self.validate_form()

  def validate_form(self):
    values = variable_decode(self.request.params)
    try:
      ### determine actual form used in this submission
      schema_id = values['type']
      schema = self.schemas[schema_id]()
    except KeyError, e:
      raise HTTPNotImplemented("Unexpected submission type!")
    try:
      form_result = schema.to_python(values[schema_id], state=self.request)
    except Invalid, error:
      log.info(error)
      self.result['values'][schema_id] = error.value or {}
      self.result['errors'][schema_id] = error.error_dict or {}
      self.request.response.status_int = 401
      return self.result
    else:
      ### if on_success returns anything else than a redirect, it must be some validation error
      resp = schema.on_success(self.request, form_result)
      self.result['values'][schema_id] = resp['values']
      self.result['errors'][schema_id] = resp['errors']
      self.request.response.status_int = 401
      return self.result