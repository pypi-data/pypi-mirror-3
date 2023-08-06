import os
import sys
import json
import math
import StringIO
import traceback
import grokpy

from exceptions import GrokError, AuthenticationError

class Stream(object):
  '''
  A Stream is the combination of data and the specification of those data
  that will be used by a model.

  * parent - Either a Client object or a Project object
  * streamDef - A python dict representing the specification of this stream
  '''

  def __init__(self, parent, streamDef):

    # Give streams access to the parent client/project and its connection
    self.parent = parent
    self.c = self.parent.c

    # Store the raw stream def in case a user wants to get it later
    self._rawStreamDef = streamDef

    # Take everything we're passed and make it an instance property.
    self.__dict__.update(streamDef)

  def addRecords(self, records, step = 500):
    '''
    Appends records to the input cache of the given stream.

    * records - A list of lists representing your data rows
    * step - How many records we will send in each request.
    '''

    # Where to POST the data
    url = self.dataUrl

    # Limit how many records we will send in a given request
    try:
      if len(records) > step:
        i = 0
        while i < len(records):
          requestDef = {"input": records[i:(i+step)]}
          if grokpy.DEBUG:
            print len(requestDef['input'])
          self.c.request('POST', url, requestDef)
          i += step
      # If it's small enough send everything
      else:
        requestDef = {"input": records}
        self.c.request('POST', url, requestDef)
    except GrokError:
      # Break recursion if this just isn't going to work
      if step < 50: raise
      # Try sending half as many records.
      step = int(math.floor(step / 2))
      self.addRecords(records, step)

  def delete(self):
    '''
    Permanently deletes this stream.

    .. warning:: There is currently no way to recover from this opperation.
    '''
    self.c.request('DELETE', self.url)

  def getSpecDict(self):
    '''
    Returns a Python dict representing the specification of this stream
    '''
    return self._rawStreamDef

  #############################################################################
  # Private methods

  def _safe_dict(self, d):
    '''
    Recursively clone json structure with UTF-8 dictionary keys

    From: http://www.gossamer-threads.com/lists/python/python/684379

    * d - A python dict.
    '''
    if isinstance(d, dict):
      return dict([(k.encode('utf-8'), self._safe_dict(v))
                    for k,v in d.iteritems()])
    elif isinstance(d, list):
      return [self._safe_dict(x) for x in d]
    else:
      return d
