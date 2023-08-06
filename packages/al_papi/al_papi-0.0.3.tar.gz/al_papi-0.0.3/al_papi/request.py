import al_papi

class Request(object):
  """
    Request class is used to handle the API calls for the Partner API.
    The three methods you can call are post, priority post and get.
    
    To make a POST to the Partner API::
      
      al_papi.Request.post({"keyword" : "Centaurs"})
    
    To make a priority POST to the Partner API you have 2 options, use the post method::
      
      al_papi.Request.post({"keyword" : "Centaurs"}, True)
    
    or use the priority_post method::
      
      al_papi.Request.priority_post({"keyword" : "Centaurs"})
    
    Please review the `Partner API Docs <http://authoritylabs.com/api/partner-api/>`_
    to get more information on the paramaters that can be passed to these methods besides
    the keyword name. The API defaults some parameters and there are additional parameters
    that can be used to specify your API requests.
  """
  
  @staticmethod
  def post(params = {}, priority = False):
    return al_papi.AlHttp.post(params, priority)
  
  @staticmethod
  def priority_post(params = {}, priority = False):
    return al_papi.AlHttp.priority_post(params)
  
  @staticmethod
  def get(params = {}):
    return al_papi.AlHttp.get(params)
  
