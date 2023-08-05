from exceptions import GrokError, AuthenticationError

class PublicDataSource(object):
  '''
  Object describing a public data source

  Currently this lives only in the client. The intent is to have a server side
  object representing a PDS as well.
  '''
  def __init__(self, connection, description):

    self.c = connection

    self.__dict__.update(description)

    self.description = description

    # A holding field that will be used by the associated stream later
    self.locationFieldName = None

  def useField(self, fieldName):
    '''
    Sets a field to be added to the data stream by this publicDataSource for
    every record passed into Grok
    '''
    for i, field in enumerate(self.description['fields']):
      if field['code'] == fieldName or field['name'] == fieldName:
        self.description['fields'][i]['useField'] = True

  def listFields(self):
    '''
    Returns a list of the names of fields currently in the PDS
    '''

    return [(field['code'],field['name']) for field in self.description['fields']]

  def setConfiguration(self, value = None, locationFieldName = None):
    '''
    Populates the 'configuration' field within the provider. What this
    configuration should be varies from provider to provider.

    See the API Reference under providerDefinitionList
    '''
    if locationFieldName:
      self.locationFieldName = locationFieldName

    if self.id == 'twitter' and value:
      if type(value) == type([]):
        value = ','.join(value)
      self.description['fields'][0]['configuration'] = value
      self.description['fields'][0]['useField'] = True
    else:
      if type(value) == type([]):
        value = ','.join(value)
      self.description['configuration'] = value
