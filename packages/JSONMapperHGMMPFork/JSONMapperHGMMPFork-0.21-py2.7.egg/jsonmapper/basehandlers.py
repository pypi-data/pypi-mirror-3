from formencode.variabledecode import variable_decode
from formencode.validators import Invalid
from pyramid.httpexceptions import HTTPNotImplemented, HTTPUnauthorized
from pyramid.view import view_config
import formencode 
from babel.numbers import parse_decimal, NumberFormatError

import logging
log = logging.getLogger(__name__)

class BaseHandler(object):
  def __init__(self, context, request):
      self.request = request
      self.context = context
      
      

class OneOfState(formencode.validators.OneOf):
    isChoice = True
    list = None
    stateKey = None
    testValueList = False
    hideList = False
    getValue = None
    getKey = None
    __unpackargs__ = ('list',)

    def getValues(self, request):
      obj = request
      for key in self.stateKey.split("."): obj = getattr(obj, key)
      return map(self.getValue, obj)
    def getKeys(self, request):
      obj = request
      for key in self.stateKey.split("."): obj = getattr(obj, key)
      return map(self.getKey, obj)
    def getItems(self, request):
      obj = request
      for key in self.stateKey.split("."): obj = getattr(obj, key)
      return [(self.getKey(elem), self.getValue(elem)) for elem in obj]

    def validate_python(self, value, state):
        self.list = self.getKeys(state)
        if self.testValueList and isinstance(value, (list, tuple)):
            for v in value:
                self.validate_python(v, state)
        else:
            if not value in self.list:
                if self.hideList:
                    raise Invalid(self.message('invalid', state), value, state)
                else:
                    try:
                        items = '; '.join(map(str, self.list))
                    except UnicodeError:
                        items = '; '.join(map(unicode, self.list))
                    raise Invalid(
                        self.message('notIn', state,
                            items=items, value=value), value, state)
      
class DecimalValidator(formencode.FancyValidator):
  messages = {"invalid_amount":'Bitte eine Zahl eingeben',
        "amount_too_high":"Bitte eine Zahl %(max_amount)s oder kleiner eingeben",
        "amount_too_low":"Bitte eine Zahl %(min_amount)s oder größer eingeben"
      }
  max = None
  min = None
  def _to_python(self, value, state):
    try:
      value = parse_decimal(value, locale = state._LOCALE_)
      if self.max and value > self.max:
        raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_decimal(self.max, locale=websession['lang'])), value, state)
      if self.min and value < self.min:
        raise formencode.Invalid(self.message("amount_too_low", state, min_amount = format_decimal(self.min, locale=websession['lang'])), value, state)
    except NumberFormatError, e:
      raise formencode.Invalid(self.message("invalid_amount", state, value = value), value, state)
    except ValueError, e:
      raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_decimal(self.max, locale=websession['lang'])), value, state)
    else: return value
      

class FullValidatedFormHandler(object):
  def __init__(self, context = None, request = None):
      self.request = request
      self.context = context
      self.result = {'values':{}, 'errors':{}, 'schemas' : self.schemas, 'formencode':formencode}
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
      self.request.session.new_csrf_token()
      return self.result
    return self.validate_form()

  def validate_form(self):
    values = variable_decode(self.request.params)
    log.debug(values)
    try:
      ### determine actual form used in this submission
      schema_id = values['type']
      schema = self.schemas[schema_id]()
    except KeyError, e:
      raise HTTPNotImplemented("Unexpected submission type!")
    try:
      form_result = schema.to_python(values[schema_id], state=self.request)
    except Invalid, error:
      log.info(error.error_dict)
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