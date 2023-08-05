'''
Base exceptions for the Grok Client Library
'''

class GrokpyError(Exception):
  pass

class AuthenticationError(GrokpyError):
  pass