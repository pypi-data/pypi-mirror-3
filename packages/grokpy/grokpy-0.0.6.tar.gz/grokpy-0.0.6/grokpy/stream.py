import os
import sys
import json
import StringIO
import traceback

from field import Field

from exceptions import GrokError, AuthenticationError

class Stream(object):
  '''
  A Stream is the combination of data and the specification of those data
  that will be used by a model
  '''

  def __init__(self, parentProject):

    # Our connection to the Grok API
    self.c = parentProject.c

    # Our stream description
    self.streamDescription = {'fields': []}

    # Our local data store
    self.records = None

    # HACK: Store contents of join file locally for bit
    self.joinFileContents = None
    self.joinFileName = None

    self.parentProject = parentProject

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
    model.startSwarm() method.
    '''

    if not self.streamDescription['fields']:
      raise GrokError('No fields found. Please configure your stream before '
                      'adding records.')
    self.records = records

    return len(self.records)

  def configure(self, filePath):
    '''
    Reads JSON from a given file and uses that to configure the stream
    '''
    fileHandle = open(filePath, 'rU')

    try:
      fields = json.load(fileHandle)
    except:
      msg = StringIO.StringIO()
      print >>msg, ("Caught JSON parsing error. Your stream specification may "
      "have errors. Original exception follows:")
      traceback.print_exc(None, msg)
      raise GrokError(msg.getvalue())

    for field in fields:
      field = self._safe_dict(field)
      self.addField(**field)

    projDesc = self.parentProject.getDescription()
    for arg, value in self.streamDescription.iteritems():
      projDesc['streamConfiguration'][arg] = value

    requestDef = {'service': 'projectUpdate',
                  'project': projDesc}

    self.c.request(requestDef, 'POST')

  def useJoinFile(self, joinFile):
    '''
    Binds a Join File to the stream and tells it how to process incoming records
    using the file.

    joinFile - A JoinFile Object
    '''
    # Make sure we have everything we need
    if not joinFile.fileKey or not joinFile.streamKey:
      raise GrokError('Please set both a fileKey and streamKey to use this '
                      'joinFile.')

    projDesc = self.parentProject.getDescription()
    primaryKeyIndex = joinFile._getFieldIndex(joinFile.fileKey)
    joinFieldIndex = self._getFieldIndex(joinFile.streamKey)

    # Turn on the fields
    for i, field in enumerate(joinFile.description['fields']):
      joinFile.description['fields'][i]['useField'] = True

    joinFile = {'name': joinFile.description['name'],
                'fields': joinFile.description['fields'],
                'primaryKeyIndex': primaryKeyIndex,
                'joinFieldIndex': joinFieldIndex,
                'joinFileId': joinFile.id}

    projDesc['joins'].append(joinFile)

    requestDef = {'service': 'projectUpdate',
                  'project': projDesc}

    newProjDesc = self.c.request(requestDef)

  def usePublicDataSource(self, publicDataSource):
    '''
    Takes a configured publicDataSource and attaches it to the stream
    '''

    # Check if there is configuration we need to complete
    if publicDataSource.locationFieldName:
      publicDataSource.description['configuration'] = \
      str(self._getFieldIndex(publicDataSource.locationFieldName))

    projDesc = self.parentProject.getDescription()
    projDesc['providers'].append(publicDataSource.description)

    requestDef = {'service': 'projectUpdate',
                  'project': projDesc}

    self.parentProject.projectDef = self.c.request(requestDef)

  #############################################################################
  # Private methods

  def _getFieldIndex(self, fieldName):
    '''
    Finds a field with a matching name and throws an error if there are more
    than one matches
    '''

    counter = 0
    index = 0
    for field in self.streamDescription['fields']:
      if field['name'] == fieldName:
        counter += 1
        index = field['index']

    if not counter:
      raise GrokError('Field not found: ' + fieldName)
    if counter > 1:
      raise GrokError('Duplicate Field Name: ' + fieldName + ' More than one '
                      'field with this name was found. Please use the '
                      'set*FieldIndex() methods directly.')


    return index

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
