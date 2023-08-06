from exceptions import GrokError

class Swarm(object):
  '''
  An object representation of the JSON swarm description the API provides.
  '''
  def __init__(self, parentModel, swarmDict):

    self.__dict__.update(swarmDict)

    # Get access to parent methods and data
    self.parentModel = parentModel

    # Connection
    self.c = self.parentModel.c

  def getState(self, url = None):
    '''
    Returns the current state of the Swarm
    '''

    if not url:
      url = self.url

    result = self.c.request('GET', url)

    if result['swarm']['status'] == 'error':
      self._handleErrors(result)

    return result['swarm']

  def _handleErrors(self, getStateResult):
    '''
    Raises a useful error from an engine level error passed through the API

    TODO: Make sure we're not leaking tracebacks.
    '''

    raise GrokError(getStateResult['swarm']['debug'])
