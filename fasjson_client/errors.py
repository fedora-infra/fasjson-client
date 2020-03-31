class BaseError(Exception):
  def __init__(self, message, code, data=None):
    super(BaseError, self).__init__(message)
    self.message = message
    self.code = code
    self.data = data

  def __repr__(self):
    return f'<{self.__class__.__name__} code={[self.code]} message={self.message} data={self.data}>'

  def __str__(self):
    return self.message


class ClientError(BaseError):
  def __init__(self, message, code, data=None):
    super(ClientError, self).__init__(message, code, data=data)