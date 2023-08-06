import al_papi

class Response(object):
  """
    Response is the class that builds up the response object after a request to
    the Partner API. It is initialized after a request and returned with information
    about your request.
    
    [Attributes]
    <success>    True/False if request was successful
    <code>       HTTP status code of request
    <body>       Body of request
    <errors>     List of RequestError objects if any
    <params>     The params of your request
    <path>       The path of the API call
    <suspended>  True/False if your API account is suspended
    <over_limit> True/False if you are over your API hourly limit
  """
  
  def __init__(self, req, path, params):
    self.success    = req.success
    self.code       = req.code
    self.body       = req.body
    self.errors     = req.errors
    self.params     = params
    self.path       = path
    self.suspended  = req.suspended
    self.over_limit = req.over_limit
  