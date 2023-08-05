import os
import httplib2
import urllib2
import json
import socket

from exceptions import GrokError, AuthenticationError

DEBUG = 0

class Connection(object):
  '''
  Connection object for the Grok Prediction Service
  '''
  
  def __init__(self, key = None, baseURL = 'http://grok-api.numenta.com'):
    
    # Search for API key in environment
    if not key or key == 'YOUR_KEY_HERE':
      key = self._find_key()
      if not key:
        raise AuthenticationError("""
          Please supply your API key.
          
          Method 1:
            Supply your credentials when you instantiate the connection.
            
            connection = %s(key='YOUR_KEY_HERE')

          Method 2:
          (More Secure)

            Add your credentials to your shell environment. From the command
            line:

            echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
            source ~/.bashrc
  
            For either method please replace the dummy key value with your real
            key from your account page.

            http://grok.numenta.com/account""" % self.__class__.__name__)
    else:
      self._validateKey(key)
        
    # The API key we'll use to authenticate all HTTP calls.
    self.key = key
    
    # The base path for all our HTTP calls
    self.baseURL = baseURL + '/version/1/'
    
    
  def request(self, requestDef, method = 'POST', body = False, headers = None):
    '''
    Interface for all HTTP requests made to the Grok API
    '''
    
    '''
    Create our HTTP client
    
    NOTE: Timeout is set by default. As this is a socket level timeout it may
    cause longpolling problems later. TODO: Re-visit
    '''
    h = httplib2.Http(".cache", 20)
    
    # Build the request
    ## GETS
    if method == 'GET':
      uri = self._requestDefToURL(requestDef)
      # Our request
      kwargs = {'uri': uri,
                'method': method,
                'headers': {}}
    ## POSTS
    elif method == 'POST':
      if body:
        # We've been given explicit body content, probably an upload
        uri = self._requestDefToURL(requestDef)
      else:      
        uri = self.baseURL
        body = {'version': '1'}
        body.update(requestDef)
        # Serialize the dict
        body = json.dumps(body)
        
      # Default to JSON for POSTs
      if not headers:
        headers = {'content-type':'application/json'}
  
      # Our request
      kwargs = {'uri': uri,
                'method': method,
                'body': body,
                'headers': headers
                }
    else:
      raise GrokError('Only GET and POST methods are currently supported.')
    
    # Add in the API key to the header of each request
    kwargs['headers'].update({'API-Key': self.key})
    
    # Make the request, handle initial connection errors
    try:
      httpResponse, content = h.request(**kwargs)
    except socket.error, e:
      if 'timed out' in e:
        raise GrokError("Request timed out. Please check the "
                        "server URL if specified, or status.numenta.com "
                        "(coming soon) if default.")
      else:
        raise GrokError(e)
    
    # Handle HTTP errors (redirects are handled by httplib2)
    if httpResponse['status'] != '200':
      raise GrokError(httpResponse)
      
    # Load info from returned JSON strings
    content = json.loads(content)
    
    if DEBUG == 1:
      print content
    
    # Some service requests don't return anything. :(
    if content != None:
      # Handle service errors
      if 'errors' in content:
        self._handleGrokErrors(content['errors']) 
      # Return good results
      try:
        result = content['result']
      # Handle non-error messages
      except KeyError:
        try:
          result = content['information'][0]
        except KeyError:
          raise GrokError('Unexpected request response:' + content)
    else:
      result = None
    
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
    
    '''
    TODO: Put this back in when we've removed the fake api key
    if len(key) < 32:
      raise AuthenticationError('This key is too short, '
                                'please check it again: "' + key +'"')
    else:
      return 'OK'
      
    '''
    pass
    
  def _handleGrokErrors(self, errors):
    '''
    Deal with known error codes from the Grok services
    '''
    raise GrokError(errors)
      
  def _requestDefToURL(self, requestDef):
    '''
    Takes in a requestDef dict and returns a uri appropriate for GET or
    for POST with body
    '''
    uriList = []
    for key, value in requestDef.iteritems():
      uriList.append(key)
      uriList.append(urllib2.quote(value))
    uriSuffix = '/'.join(uriList)
    uri = self.baseURL + uriSuffix
    
    return uri