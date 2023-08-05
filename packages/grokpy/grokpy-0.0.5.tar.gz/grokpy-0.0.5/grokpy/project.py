from model import Model
from stream import Stream

from exceptions import GrokError, AuthenticationError

class Project(object):
  '''
  Object representing a Grok project
  '''
  
  def __init__(self, connection, projectDef):
    
    self.c = connection
    self.id = str(projectDef['id'])
    self.name = projectDef['name']
    self.projectDef = projectDef
    
  def getDescription(self):
    '''
    Get the current state of the project from Grok
    '''
    requestDef = {'service': 'projectRead',
                  'projectId': self.id}
    
    return self.c.request(requestDef)
    
  def delete(self):
    '''
    Permanently deletes the project, all its models, and data.
    '''
    requestDef = {'service': 'projectDelete',
                  'projectId': self.id}
    
    return self.c.request(requestDef)
  
  def setName(self, newName):
    '''
    Rename the project
    '''
    # Get current description
    desc = self.getDescription()
    
    # Modify the dictionary
    desc['name'] = newName
    
    requestDef = {'service': 'projectUpdate',
                  'project': desc}
    
    return self.c.request(requestDef, 'POST')
    
  def createModel(self):
    '''
    Create a model associated with this project
    '''
    
    '''
    WARNING: HACK
    
    Due to the current object model we don't actually create the model until
    we associate a stream with the model
    '''
    
    return Model(self.c, self.projectDef)
  
  def getModel(self, modelId):
    '''
    Returns the model corresponding to the given modelId
    '''
    if modelId == 'YOUR_MODEL_ID_HERE':
      raise GrokError('Please supply a valid model id')
    
    # Determine if this is a search or production model
    productionModels = [model['id'] for model in self._listProductionModels()]
    searchModels = [model['id'] for model in self._listSearchModels()]
    
    if modelId in productionModels and modelId in searchModels:
      raise GrokError('Ruh-ro, model id collision between prod and search.')
    elif modelId in productionModels:
      modelType = 'production'
    elif modelId in searchModels:
      modelType = 'search'
    else:
      raise GrokError('Model Id not found.')

    # Get the model definition and create a new Model object with that.
    service = modelType + 'ModelRead'
    idParam = modelType + 'ModelId'
    
    requestDef = {'service': service,
                  idParam: modelId}
    
    modelDef = self.c.request(requestDef, 'POST')
    
    return Model(self.c, self.projectDef, modelDef = modelDef)
  
  def stopAllModels(self):
    '''
    A convenience method to stop all models that have been promoted
    '''
    
    productionModels = self._listProductionModels()
    
    for model in productionModels:
      if model['running']:
        id = model['id']
        print 'Stopping model: ' + id
        requestDef = {'service': 'productionModelStop',
                      'productionModelId': id}
        self.c.request(requestDef)
    
  def createStream(self):
    '''
    Returns an instance of the Stream object
    '''
    
    return Stream()
    
  #############################################################################
  # Private methods
  
  
  def _listProductionModels(self):
    '''
    Returns a list of all production models.
    '''
    
    requestDef = {'service': 'productionModelList',
                  'projectId': self.id,
                  'includeTotalCount': False}
    
    response = self.c.request(requestDef, 'POST')
    
    return response['productionModels']
  
  def _listSearchModels(self):
    '''
    Returns a list of all search models
    '''
    
    requestDef = {'service': 'searchModelList',
                  'projectId': self.id,
                  'includeTotalCount': False}
    
    response = self.c.request(requestDef, 'POST')
    
    return response['searchModels']