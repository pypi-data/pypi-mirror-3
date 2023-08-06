import al_papi

from httplib2 import Http
from urllib import urlencode
import re
import simplejson as json

class AlHttp(object):
  """
    AlHttp is used by the Request class to make the raw HTTP requests to the API.
    Please use the Request class to make post, priority_post and get calls to the API.
  """
  
  post_path     = "/keywords.json"
  get_path      = "/keywords/get.json"
  priority_path = "/keywords/priority.json"
  
  def __init__(self):
    self.success    = False
    self.over_limit = False
    self.suspended  = False
    self.errors     = []
    self.code       = None
    self.body       = None
  
  @staticmethod
  def default_headers():
    return { 'Content-type': 'application/json' }
  
  @staticmethod
  def post(params = {}, priority = False):
    path = al_papi.AlHttp.post_path if priority == False else al_papi.AlHttp.priority_path
    return al_papi.AlHttp.request("POST", params, path)
  
  @staticmethod
  def priority_post(params = {}):
    return al_papi.AlHttp.request("POST", params, al_papi.AlHttp.priority_path)
  
  @staticmethod
  def get(params = {}):
    return al_papi.AlHttp.request("GET", params, al_papi.AlHttp.get_path)
  
  @staticmethod
  def request(verb, params, path):
    req  = AlHttp()
    http = Http()
    
    params.update( { "auth_token" : al_papi.Config.api_key } )
    keyword = params.get("keyword", "")
    keyword = unicode(keyword, 'utf-8')
    params.update( { "keyword" : keyword.encode('utf-8') })
    url = '%s%s?%s' % ( al_papi.Config.default_host, path, urlencode(params) )
    resp, content = http.request(url, verb, headers=al_papi.AlHttp.default_headers())
    
    status   = resp["status"]
    req.code = status
    req.body = content
    content = unicode(content, "ISO-8859-1")
    
    if status == "200":
      req.success = True
      req.body = json.loads(content)
    elif status == "204":
      req.errors.append(al_papi.RequestError('No Content', status))
    elif status == "401":
      req.errors.append(al_papi.RequestError('Invalid Auth Token Provided', status))
    elif status == "403":
      if re.search("Account Suspended", content, re.I):
        req.suspended
        req.errors.append(al_papi.RequestError('Account Suspended', status))
      elif re.search("Request Limit Exceeded", content, re.I):
        req.over_limit = True
        req.errors.append(al_papi.RequestError('Request Limit Exceeded', status))
    else:
      try:
        req.body = json.loads(content)
      except:
        req.body = content
      
      req.errors.append(al_papi.RequestError(req.body, status))
    
    return al_papi.Response(req, path, params)
