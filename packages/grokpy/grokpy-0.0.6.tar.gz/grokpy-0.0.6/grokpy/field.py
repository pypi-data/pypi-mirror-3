import inspect
import json
import copy

class Field(object):
  '''
  A complex object specification which allows Grok to properly interpret
  input data.
  '''
  
  def __init__(self, **kwargs):
    
    defaultDescription = {
        "aggregationFunction":"first",
        "dataFormat":{
          "dataType":"SCALAR",
          "formatString": None
        },
        "dataType":"SCALAR",
        "fieldRange": None,
        "fieldSubset": None,
        "flag":"NONE",
        "name": None,
        "useField": True
      }
    
    # Create a dictionary describing this field
    self.fieldDescription = defaultDescription
    
    for arg, value in kwargs.iteritems():
      self.fieldDescription[arg] = value

