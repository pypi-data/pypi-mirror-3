"""This package is a python wrapper for the ordr.in API. The main developer
documentation for this API is located at http://ordr.in/developers"""
import restaurant, user, order

class APIs(object):

  def __init__(self, api_key, restaurant_url=None, user_url=None, order_url=None):
    """Sets up this module to make API calls. The first argument is the developer's
    API key. The other three are the URLs corresponding to the three parts of the api.
    No API calls will work until this function is called. API objects will only be
    instantiated for URLs that are passed in.

    Arguments:
    api_key -- The developer's API key

    Keyword Arguments:
    restaurant_url -- The base url for the restaurant API
    user_url -- The base url for the user API
    order_url -- The base url for the order API

    """
    if restaurant_url:
      self.restaurant = restaurant.RestaurantApi(api_key, restaurant_url)
    if user_url:
      self.user = user.UserApi(api_key, user_url)
    if order_url:
      self.order = order.OrderApi(api_key, order_url)
