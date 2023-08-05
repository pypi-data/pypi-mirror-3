import json

from field import Field

from exceptions import GrokError, AuthenticationError

class Stream(object):
  '''
  A Stream is the combination of data and the specification of those data
  that will be used by a model
  '''

  def __init__(self):
    # Our stream description
    self.streamDescription = {'fields': []}
    
    # Our local data store
    self.records = None
  
  def addField(self, **kwargs):
    '''
    Add a field object to a stream
    '''
    newField = Field(**kwargs)

    self.streamDescription['fields'].append(newField.fieldDescription)
    
    return newField
    
  def addRecords(self, records):
    '''
    Appends records to the input cache of the given stream.
    
    WARNING: HACK
    
    Due to the current object model we actually send the records in the
    model.addStream() method.
    '''
    
    self.records = records
    
    return len(self.records)
    
  def configure(self, filePath):
    '''
    Reads JSON from a given file and uses that to configure the stream
    '''
    fileHandle = open(filePath, 'rU')
    fields = json.load(fileHandle)
    
    for field in fields:
      field = self._safe_dict(field)
      self.addField(**field)

  def _safe_dict(self, d): 
    '''
    Recursively clone json structure with UTF-8 dictionary keys
    
    From: http://www.gossamer-threads.com/lists/python/python/684379
    '''
    if isinstance(d, dict): 
      return dict([(k.encode('utf-8'), self._safe_dict(v)) for k,v in d.iteritems()]) 
    elif isinstance(d, list): 
      return [self._safe_dict(x) for x in d] 
    else: 
      return d 