
import grokpy

from grokpy.exceptions import GrokError

class TwitterDataSource(object):
  '''
  A specification object for adding Twitter data to your stream
  '''

  def __init__(self):

    # Our list of fields in this source
    self.fields = []

  def addKeyword(self, keyword):
    '''
    Adds a keyword to the list of keywords to be merged with the parent stream.

    * keyword - A string without spaces or boolean logic.

    Valid Examples::

      twitter = TwitterDataSource()
      twitter.addKeyword('happy')
      twitter.addKeyword('@google')
      twitter.addKeyword('#ThingsThatRule)

    Invalid Examples::

      twitter = TwitterDataSource()
      twitter.addKeyword('this has spaces')
      twitter.addKeyword('george AND sally')
    '''

    if keyword.find(' ') != -1:
      raise GrokError('Twitter keywords cannot contain spaces')

    fieldSpec = {"name": keyword,
                  "dataFormat": {"dataType":
                   grokpy.DataType.SCALAR}}

    self.fields.append(fieldSpec)

  def addKeywords(self, keywords):
    '''
    Adds each keyword in the list `keywords` to the datasource

    * keywords - A list of keywords to be added.
    '''
    for keyword in keywords:
      self.addKeyword(keyword)

  def getSpec(self):
    '''
    Returns an assembled dict from the current state of the specification.
    Usually consumed by an instance of the StreamSpecification class.
    '''

    returnSpec = {"name": "Twitter",
                 "dataSourceType": "public",
                 "fields": self.fields}

    return returnSpec
