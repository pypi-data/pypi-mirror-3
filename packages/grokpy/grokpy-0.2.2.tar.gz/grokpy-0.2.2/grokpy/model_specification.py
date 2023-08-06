import grokpy

from grokpy.exceptions import GrokError

class ModelSpecification(object):
  '''
  This is a client level object that is useful for building Model
  Specifications in an object oriented way. (As opposed to writing the JSON
  or Dict directly).
  '''

  def __init__(self):

    # What is the name of this model
    self.name = ''

    # What stream should this model listen to
    self.streamId = None

    # What aggregation will this model use
    self.aggInt = None

    # List of steps into the future to predict
    self.steps = [1]

  def setName(self, name):
    '''
    Updates the local name.
    '''
    self.name = name

  def setPredictedField(self, predictedField):
    '''
    Sets the field the model will attempt to predict. Swarm will evaluate
    models based on the models ability to predict this field.

    * predictedField - String. A field name as it appears in the stream
      specification.
    '''

    self.predictedField = predictedField

  def setStream(self, streamId):
    '''
    Sets which stream the model will listen to.

    * streamId - String. A 36 unique id for a Stream. OR grokpy.Stream object
      from which a stream id will be extracted.
    '''

    if isinstance(streamId, grokpy.Stream):
      self.streamId = streamId.id
    elif len(streamId) == 36:
      self.streamId = streamId
    else:
      raise GrokError('This does not appear to be a properly formatted stream '
                      'id.')

  def setAggregationInterval(self, aggInt):
    '''
    Defines the interval Grok will use to aggregate incoming records over.

    * aggInt - Dict.

    Example::

        interval = {'hours': 1,
                    'minutes': 15}

        modelSpec.setAggregationInterval(interval)
    '''
    self.dataSources.append(dataSource)

  def setPredictionSteps(self, steps = [1]):
    '''
    Adds a list of steps in the future to predict.

    * steps - A list of integers. The default is to predict one timestep into
              the future.

    Example Usage::

      To get predictions for the next three timesteps

      model.setPredictionSteps([1,2,3])

      To get predictions for the next three timesteps where you care most
      about accuracy three steps out

      model.setPredictionSteps([3,1,2])

      The first item in the list is the optimized timestep. The swarm will find
      a model that does best at predicting that number of steps into the future.
    '''

    if not steps:
      raise GrokError('Steps be a list and have at least one value.')

    if len(steps) > 10:
      raise GrokError('Max number of values for "steps" is 10. Note you can '
                      'request 20 steps into the future (steps = [20]), just '
                      'not all 20 at once (steps = [1, ... 20]')

    self.steps = steps

  def getSpec(self):
    '''
    Returns an assembled dict from the current state of the specification
    '''

    if not self.name:
      raise GrokError('Please set a name for this model')

    if not self.streamId:
      raise GrokError('Please set a stream id for this model spec.')

    returnSpec = {"name": self.name,
                  "predictedField": self.predictedField,
                  "streamId": self.streamId,
                  "predictionSteps": self.steps}

    if self.aggInt:
      returnSpec['aggregation'] = {}
      returnSpec['aggregation']['interval'] = self.aggInt

    return returnSpec
