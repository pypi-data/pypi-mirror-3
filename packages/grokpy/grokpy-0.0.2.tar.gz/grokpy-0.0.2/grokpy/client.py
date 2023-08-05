import os
import urllib2
import json

from grokpy.exceptions import (GrokpyError,
                               AuthenticationError)

class Client(object):
  '''
  Client for the Grok Prediction Service
  
  This class wraps services provided by the Grok API
  '''
  
  def __init__(self, key = None,
               baseURL = 'http://107.22.53.125:1961/version/1/'):
    '''
    Instantiate a Grok client
    '''
    
    # Search for API key in environment
    if not key:
      key = find_key()
      if not key:
        raise AuthenticationError("""
          Please supply your API key.
          
          Method 1:
            Supply your credentials when you instantiate the client.
            
            client = %s(key='D23984KJHKJH')

          Method 2:
          (More Secure)

            Add your credentials to your shell environment. From the command
            line:

            echo "export GROK_API_KEY=D23984KJHKJH" >> ~/.bashrc
            source ~/.bashrc
  
            For either method please replace the dummy key value with your real
            key from your account page.

            http://grok.numenta.com/account""" % self.__class__.__name__)
        
    # The API we'll use to authenticate all HTTP calls.
    self.key = key
    
    # The base path for all our HTTP calls
    self.baseURL = baseURL + 'apiKey/' + self.key + '/'
    
  def request(self, path, method = None):
    '''
    Make a call directly to the Grok API and print the returned JSON
    '''
    uri = self.baseURL + path
    print uri
    
    rv = urllib2.urlopen(uri)
    
    pyResults = json.loads(rv.read())
    
    return pyResults['result']
    
  #############################################################################
  # API Services
  
  def availableServices(self):
    '''
    Returns a list of the Grok Services
    '''
    return self.request('')
  
  def cachePurge(self):
    pass
  
  def dataUpload(self):
    pass

  def dataUploadInit(self):
    pass
  
  def dataUploadProgress(self):
    pass
  
  def inputCacheAppend(self):
    pass
  
  def inputCacheData(self):
    pass

  def joinedDataService(self):
    pass
  
  '''
  MODELS
  '''
  
  def modelCopy(self):
    pass
  
  def modelCreate(self):
    pass
  
  def modelDelete(self):
    pass
  
  def modelList(self):
    pass
  
  def modelPredictions(self):
    pass
  
  def modelRead(self):
    pass
  
  def modelUpdate(self):
    pass
  
  '''
  PROJECTS
  '''
  
  def createProject(self, name):
    
    return self.request('service/projectCreate/name/' + name)
  
  def projectDelete(self):
    pass
  
  def projectList(self):
    pass
  
  def readProject(self, projectId):
    
    return self.request('service/projectRead/projectId/' + str(projectId))
  
  def projectUpdate(self):
    pass
  
  '''
  PROVIDERS
  '''
  
  def providerFileDelete(self):
    pass
  
  def providerFileList(self):
    pass
  
  def providerFileUpload(self):
    pass
  
  def providerList(self):
    '''
    Get a list of available data providers and the specification for using them
    as part of a search
    '''
    
    self.request('service/providerList')
  
  '''
  SEARCH
  '''
  
  def searchCacheData(self):
    pass

  def searchCancel(self):
    pass
  
  def searchList(self):
    pass
  
  def searchProgress(self):
    pass
  
  def searchResult(self):
    pass
  
  def searchStart(self):
    pass
        
def find_key():
  '''
  Retrieve an API key from the user's shell environment
  '''
  try:
    key = os.environ["GROK_API_KEY"]
  except KeyError:
    return None
  
  return key