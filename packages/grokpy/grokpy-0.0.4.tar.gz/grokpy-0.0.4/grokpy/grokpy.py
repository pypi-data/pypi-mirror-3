from connection import Connection
from project import Project

class Grokpy(object):
  '''
  Top level object for interacting with the Grok Prediction Service from
  Numenta
  '''
  
  def __init__(self, key = None,
               baseURL = 'http://api.numenta.com:1961/version/1/',
               credentials = {}):
    '''
    TODO: Make this into a singleton? Do we need to support multiple
    accounts in the same process?
    '''    
    # Create a connection to the API
    self.c = Connection(key, baseURL, credentials)
  
  
  def createProject(self, projectName):
    '''
    Creates a project through the Grok API
    '''
    
    # A dictionary describing the request
    requestDef = {
      'service': 'projectCreate',
      'name': projectName,
    }
    
    # Make the API request
    result = self.c.request(requestDef)
    
    # Use the results to instantiate a new Project object
    project = Project(self.c, result)
    
    return project
  
  def listProjects(self):
    '''
    Lists all the projects currently associated with this account
    '''
    requestDef = {'service': 'projectList'}
    
    projectDescriptions = self.c.request(requestDef)
    
    # Create objects out of the returned descriptions
    projects = [Project(self.c, pDef) for pDef in projectDescriptions]
      
    return projects