import al_papi

class WebInsight(object):
  """
    Request class is used to handle the API calls for the Partner API.
    The three methods you can call are post, priority post and get.

    To make a POST to the Partner API Web Insight::

      al_papi.WebInsight.post({"url" : "http://www.qwiki.com", "callback" : "http://your-callback.com"})

    To make a GET from the Partner API Web Insight::

      al_papi.WebInsight.get({"url" : "http://www.qwiki.com", "date_created" : "2012-06-14", "time_created" : "01:50"})

    Please review the `Partner API Docs <http://authoritylabs.com/api/partner-api/>`_
    to get more information on the paramaters that can be passed to these methods besides
    the keyword name. The API defaults some parameters and there are additional parameters
    that can be used to specify your API requests.
  """

  @staticmethod
  def post(params = {}):
    return al_papi.AlHttp.post(params, '/web/insight.json')

  @staticmethod
  def get(params = {}):
    return al_papi.AlHttp.get(params, '/web/insight.json')
