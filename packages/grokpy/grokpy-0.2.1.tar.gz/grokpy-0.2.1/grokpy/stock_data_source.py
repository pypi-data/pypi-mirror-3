import grokpy

from grokpy.exceptions import GrokError

class StockDataSource(object):
  '''
  A specification object for adding Stock data to your stream

  Stock data is available as daily records.
  '''

  def __init__(self):

    # Our list of fields in this source
    self.fields = []

  def addSymbol(self, symbol):
    '''
    Adds a ticker symbol to the list of symbols to be merged with the parent
    stream.

    * symbol - A valid ticker symbol
    '''

    fieldSpec = {"name": keyword,
                  "dataFormat": {"dataType":
                   grokpy.DataType.SCALAR}}

    self.fields.append(fieldSpec)

  def addSymbols(self, keywords):
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
