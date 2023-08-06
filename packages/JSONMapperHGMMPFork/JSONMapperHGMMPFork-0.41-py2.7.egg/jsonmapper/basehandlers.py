from formencode.variabledecode import variable_decode
from formencode.validators import Invalid
from pyramid.httpexceptions import HTTPNotImplemented, HTTPUnauthorized
from pyramid.view import view_config
from BeautifulSoup import BeautifulSoup
import formencode 
from babel.numbers import parse_decimal, format_decimal, NumberFormatError

import logging
log = logging.getLogger(__name__)

class BaseHandler(object):
  def __init__(self, context, request):
      self.request = request
      self.context = context
      
      
     
      
class SanitizedHTMLString(formencode.validators.String):
  messages = {"invalid_format":'There was some error in your HTML!'}
  valid_tags = ['a','strong', 'em', 'p', 'ul', 'ol', 'li', 'br', 'b', 'i', 'u', 's', 'strike', 'font', 'pre', 'blockquote', 'div']
  valid_attrs = ['size', 'color', 'face', 'title', 'align']
  def sanitize_html(self, html):
      soup = BeautifulSoup(html)
      for tag in soup.findAll(True):
          if tag.name.lower() not in self.valid_tags:
              tag.extract()
          elif tag.name.lower() != "a":
              tag.attrs = [attr for attr in tag.attrs if attr[0].lower() in self.valid_attrs]
          else:
              attrs = dict(tag.attrs)
              tag.attrs = [('href', attrs.get('href')), ('target', '_blank')]
      val = soup.renderContents()
      return val.decode("utf-8")
  def _to_python(self, value, state):
    value = super(self.__class__, self)._to_python(value, state)
    try:
      return self.sanitize_html(value)
    except Exception, e:
      log.error("HTML_SANITIZING_ERROR %s", value)
      raise formencode.Invalid(self.message("invalid_format", state, value = value), value, state)

class OneOfState(formencode.validators.OneOf):
    isChoice = True
    list = None
    stateKey = None
    testValueList = False
    hideList = False
    getValue = None
    getKey = None
    custom_attribute = 'custom'
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
      return obj
    def hasCustom(self, request):
      return len(filter(None, map(lambda item: getattr(item, self.custom_attribute, False),self.getItems(request)))) > 0
    
    def _to_python(self, value, state):
        if isinstance(value, dict):
          custom = value.get("custom", None)
          val = value.get("value", None)
          items = {self.getKey(s):getattr(s, self.custom_attribute, False) for s in self.getItems(state)}
          is_custom = items.get(val, False)
        else:
          val = value
        self.list = self.getKeys(state)
        if not val in self.list:
            if self.hideList:
                raise Invalid(self.message('invalid', state), val, state)
            else:
                try:
                    items = '; '.join(map(str, self.list))
                except UnicodeError:
                    items = '; '.join(map(unicode, self.list))
                raise Invalid(
                    self.message('notIn', state,
                        items=items, val=val), val, state)
        else:
          return custom if is_custom and custom else val
    
    validate_python = formencode.FancyValidator._validate_noop
class OneOfStateNoCustom(OneOfState):
    def hasCustom(self, req):
        return False
      
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
        raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_decimal(self.max, locale=state._LOCALE_)), value, state)
      if self.min and value < self.min:
        raise formencode.Invalid(self.message("amount_too_low", state, min_amount = format_decimal(self.min, locale=state._LOCALE_)), value, state)
    except NumberFormatError, e:
      raise formencode.Invalid(self.message("invalid_amount", state, value = value), value, state)
    except ValueError, e:
      raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_decimal(self.max, locale=state._LOCALE_)), value, state)
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
    self.request.session.get_csrf_token()
    add_globals = getattr(self, "add_globals", None)
    if(add_globals is not None):
      self.result = add_globals(self.request, self.result)
    prepop = getattr(self, "pre_fill_values", None)
    if(prepop is not None):
      self.result = prepop(self.request, self.result)
    return self.result

  @view_config(request_method='POST')
  def POST(self):
    req = self.request
    if req.params.get('token') != req.session.get_csrf_token():
      self.request.session.get_csrf_token()
      add_globals = getattr(self, "add_globals", None)
      if(add_globals is not None):
        self.result = add_globals(self.request, self.result)
      return self.result
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
      log.error(error.error_dict)
      self.result['values'][schema_id] = error.value or {}
      self.result['errors'][schema_id] = error.error_dict or {}
      self.request.response.status_int = 401
    else:
      ### if on_success returns anything else than a redirect, it must be some validation error
      resp = schema.on_success(self.request, form_result)
      self.result['values'][schema_id] = resp['values']
      self.result['errors'][schema_id] = resp['errors']
      self.request.response.status_int = 401
    add_globals = getattr(self, "add_globals", None)
    if(add_globals is not None):
      self.result = add_globals(self.request, self.result)
    return self.result
