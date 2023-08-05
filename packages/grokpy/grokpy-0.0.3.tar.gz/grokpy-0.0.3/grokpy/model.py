class Model(object):
  '''
  Object representing a Grok Model
  '''

  def __init__(self, connection, modelDef):
    # Our connection to the Grok API
    self.c = connection