
import grokpy

from grokpy.exceptions import GrokError

class WeatherDataSource(object):
  '''
  A specification object for adding Weather data to your stream
  '''

  def __init__(self):

    # Our list of fields in this source
    self.fields = []

  def addMeasurement(self, measurementType):
    '''
    Adds a keyword to the list of keywords to be merged with the parent stream.

    * measurementType - A grokpy.WeatherDataType enum value
    '''
    
    if measurementType not in grokpy.WeatherDataType.__dict__.values():
      raise GrokError('The provided measurement type is not recognized: ' +
                      str(measurementType))

    fieldSpec = {"name": measurementType,
                  "dataFormat": {"dataType": grokpy.DataType.SCALAR}}

    self.fields.append(fieldSpec)

  def getSpec(self):
    '''
    Returns an assembled dict from the current state of the specification.
    Usually consumed by an instance of the StreamSpecification class.
    '''

    returnSpec = {"name": "Weather",
                 "dataSourceType": "public",
                 "fields": self.fields}

    return returnSpec
