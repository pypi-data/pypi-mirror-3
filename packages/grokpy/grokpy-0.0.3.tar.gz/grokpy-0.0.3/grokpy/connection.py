import os
import httplib2
import urllib2
import json
import socket

from exceptions import *

class Connection(object):
  '''
  Connection object for the Grok Prediction Service
  '''
  
  def __init__(self, key = None,
               baseURL = 'http://api.numenta.com:1961/',
               credentials = {}):
    
    # Search for API key in environment
    if not key:
      key = self._find_key()
      if not key:
        raise AuthenticationError("""
          Please supply your API key.
          
          Method 1:
            Supply your credentials when you instantiate the connection.
            
            connection = %s(key='D23984KJHKJH')

          Method 2:
          (More Secure)

            Add your credentials to your shell environment. From the command
            line:

            echo "export GROK_API_KEY=D23984KJHKJH" >> ~/.bashrc
            source ~/.bashrc
  
            For either method please replace the dummy key value with your real
            key from your account page.

            http://grok.numenta.com/account""" % self.__class__.__name__)
    else:
      self._validateKey(key)
        
    # The API key we'll use to authenticate all HTTP calls.
    self.key = key
    
    # The base path for all our HTTP calls
    self.baseURL = baseURL + 'version/1/apiKey/' + self.key + '/'
    
    # If we were given credentials use them
    self.credentials = credentials
    
  def request(self, requestDef, method = 'GET', body = False):
    '''
    Interface for all HTTP requests made to the Grok API
    '''
    
    # Create our HTTP client
    h = httplib2.Http(".cache")
    if self.credentials:
      name = self.credentials['name']
      password = self.credentials['password']
      print name, password
      h.add_credentials(name, password)
    
    # Build the request
    if method == 'GET':
      uriList = []
      for key, value in requestDef.iteritems():
        uriList.append(key)
        uriList.append(urllib2.quote(value))
      uriSuffix = '/'.join(uriList)
      uri = self.baseURL + uriSuffix
      # Our request
      kwargs = {'uri': uri,
                'method': method}
        
    elif method == 'POST':
      uri = self.baseURL
      body = {'version': '1',
              'apiKey': self.key}
      body.update(requestDef)
      # Serialize the dict
      body = json.dumps(body)
      # Our request
      kwargs = {'uri': uri,
                'method': "POST",
                'body': body,
                'headers': {'content-type':'application/json'}
                }
    else:
      raise GrokError('Only GET and POST methods are currently supported.')
      
    # Make the request, handle errors
    try:
      httpResponse, content = h.request(**kwargs)
    except socket.error, e:
      raise GrokError(e)
      
    # Load info from returned JSON strings
    content = json.loads(content)
    
    # Useful information is in the result object
    try:
      result = content.get('result')
    except AttributeError:
      # Call returned None
      result = None
    
    print httpResponse
    print result
    
    return result
  
  ###########################################################################
  # Private Methods
    
  def _find_key(self):
    '''
    Retrieve an API key from the user's shell environment
    '''
    try:
      key = os.environ["GROK_API_KEY"]
    except KeyError:
      return None
    
    return key

  def _validateKey(self, key):
    '''
    Makes sure that a given key conforms to the expected format
    '''
    
    if len(key) < 32:
      raise AuthenticationError('This key is too short, '
                                'please check it again: "' + key +'"')
    else:
      return 'OK'