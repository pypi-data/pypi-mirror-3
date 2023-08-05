import os
import csv
import StringIO
import traceback
import json

from model import Model
from stream import Stream

from exceptions import GrokError, AuthenticationError

class JoinFile(object):
  '''
  Object representing a Join File within a Project
  '''

  def __init__(self, parentProject, description):

    self.c = parentProject.c

    self.parentProjectId = parentProject.id

    self.description = description

    self.id = self.description['id']

    self.name = self.description['name']

    # Primary key in file
    self.fileKey = None

    # Join field
    self.streamKey = None

  def delete(self):
    '''
    Permanently deletes this Join File
    '''

    requestDef = {'service': 'joinFileDelete',
                  'projectId': self.parentProjectId,
                  'joinFileId': self.id}

    self.c.request(requestDef)

  def setFileKey(self, key):
    '''
    The field to use as primary key in the file
    '''
    self.fileKey = key

  def setStreamKey(self, key):
    '''
    The field in each stream record to attempt to pair with the fileKey
    '''
    self.streamKey = key


  #############################################################################
  # Private methods

  def _getFieldIndex(self, fieldName):
    '''
    Finds a field with a matching name and throws an error if there are more
    than one matches
    '''

    counter = 0
    index = 0
    for field in self.description['fields']:
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
