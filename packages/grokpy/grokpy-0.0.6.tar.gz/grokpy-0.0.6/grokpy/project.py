import os
import csv
import StringIO
import traceback
import json

from model import Model
from stream import Stream
from joinFile import JoinFile

from exceptions import GrokError, AuthenticationError

class Project(object):
  '''
  Object representing a Grok project
  '''

  def __init__(self, connection, projectDef):

    self.c = connection
    try:
      self.id = projectDef['id']
      self.id = str(self.id)
      self.name = projectDef['name']
    except TypeError:
      raise GrokError('Instantiating a project expects a dictionary')
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
    we start a swarm
    '''

    return Model(self)

  def getModel(self, modelId):
    '''
    Returns the model corresponding to the given modelId
    '''
    if modelId == 'YOUR_MODEL_ID':
      raise GrokError('Please supply a valid Model Id')

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

    return Model(self, modelDef = modelDef)

  def listModels(self):
    '''
    Returns a list of Models that exist in this project
    '''
    searchModelDefs = self._listSearchModels()
    prodModelDefs = self._listProductionModels()

    modelDescriptions = searchModelDefs.append(prodModelDefs)

    if modelDescriptions:
      models = [Model(self.c, self.projectDef) for model in modelDescriptions]
    else:
      models = []

    return models

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

    return Stream(self)

  def createJoinFile(self, dataFilePath, specFilePath):
    '''
    Uploads the contents of a csv file which can be used to programatically
    add fields to records in a stream.
    '''
    # Get data
    _, filename = os.path.split(dataFilePath)
    dataHandle = open(dataFilePath, 'rU')
    joinFileContents = [row for row in csv.reader(dataHandle)]
    dataHandle.close()
    # Get spec

    specHandle = open(specFilePath, 'rU')
    try:
      fields = json.load(specHandle)
    except:
      msg = StringIO.StringIO()
      print >>msg, ("Caught JSON parsing error. Your stream specification may "
      "have errors. Original exception follows:")
      traceback.print_exc(None, msg)
      raise GrokError(msg.getvalue())
    specHandle.close()

    requestDef = {'service': 'joinFileCreate',
                  'projectId': self.id,
                  'name': filename,
                  'fields': fields,
                  'data': joinFileContents}

    response = self.c.request(requestDef, 'POST')

    return JoinFile(self, response)

  def delete(self):
    '''
    Permanently deletes this project, its models and streams
    TODO: Verify with new OM
    '''

    requestDef = {'service': 'projectDelete',
                  'projectId': self.id}

    self.c.request(requestDef)

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
