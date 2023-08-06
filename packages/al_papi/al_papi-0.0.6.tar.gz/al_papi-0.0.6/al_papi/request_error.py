import al_papi

class RequestError(object):
  """
    RequestError is a class that is used when requests have errors to the API.
    It holds the message of the error and the HTTP status code of the request.
    
    [Attributes]
    <code>    HTTP status code of request
    <message> Message of the error
  """
  def __init__(self, message, code):
    self.message = message
    self.code    = code
    