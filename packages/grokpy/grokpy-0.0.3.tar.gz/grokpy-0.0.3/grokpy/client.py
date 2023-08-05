import os
import urllib
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
               baseURL = 'http://50.19.178.199:1961/version/1/'):
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
    
  def request(self, path, returns = True):
    '''
    Make a call directly to the Grok API and print the returned JSON
    '''
    uri = self.baseURL + path
    print uri
    
    if returns:
      rv = urllib2.urlopen(uri)
      pyResults = json.loads(rv.read())
      if pyResults.get('result'):
        return pyResults['result']
      else:
        return pyResults
    else:
      urllib2.urlopen(uri)
      return
    
  #############################################################################
  # API Methods
  
  def cachePurge(self):
    pass
  
  def dataUpload(self):
    pass

  def initDataUpload(self):
    pass
  
  def dataUploadProgress(self):
    pass
  
  def appendToInputCache(self):
    pass
  
  def inputCacheData(self):
    pass

  def joinedDataService(self):
    pass
  
  '''
  MODELS
  '''
  
  def copyModel(self):
    pass
  
  def createModel(self, projectId, modelName):
    '''
    Creates a new model
    '''
    modelName = urllib.quote(modelName)
    return self.request('service/searchModelCreate/projectId/' + str(projectId) + '/name/' + modelName)
    
  def deleteModel(self):
    pass
  
  def listModels(self):
    pass
  
  def modelPredictions(self):
    pass
  
  def readFromModel(self):
    pass
  
  def updateModel(self):
    pass
  
  '''
  PROJECTS
  '''

  def createProject(self, name):
    
    name = urllib.quote(name)
    return self.request('service/projectCreate/name/' + name)
  
  def deleteProject(self, projectId):
    '''
    Deletes a project with the given id
    '''
    returns = False
    return self.request('service/projectDelete/projectId/' + str(projectId), returns)    
  
  def listProjects(self):
    '''
    Returns a list of project objects. Each object is like calling
    projectInfo() on each project
    '''
    
    return self.request('service/projectList')
    
  def projectInfo(self, projectId):
    '''
    Returns a dictionary containing project meta data
    '''
    
    return self.request('service/projectRead/projectId/' + str(projectId))
  
  def updateProject(self):
    pass
  
  '''
  PROVIDERS
  '''
  
  def deleteProviderFile(self):
    pass
  
  def listProviderFiles(self):
    pass
  
  def uploadProviderFile(self):
    pass
  
  def listProviders(self):
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

  def cancelSearch(self):
    pass
  
  def listSearches(self):
    pass
  
  def searchProgress(self):
    pass
  
  def searchResult(self):
    pass
  
  def startSearch(self):
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