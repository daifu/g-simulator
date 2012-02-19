# Message class
# it provides message implementation for servent
#
class Message:
  def __init__(self, ttl = 7, hops = 0, body = None):
    self.ttl = ttl
    self.hops = hops
    self.body = body

  def setBody(self, body):
    self.body = body

  def getBody(self):
    return self.body

  def setPayloadLength(self, length):
    self.payloadLength = length

  def getPayloadLength(self):
    return self.payloadLength
  
  def setPayloadDescriptor(self, descriptor):
    """Msg body can be determined based on payload descriptor"""
    self.payloadDescriptor = descriptor
    self.messageBody = MessageBody(descriptor)

  def getPayloadDescriptor(self):
    return self.payloadDescriptor

  def getMessageBody(self):
    return self.messageBody

  def serialize(self, raw_byte_iterator):
    """Todo: how to serialize?? what is the input and output"""
    pass


# MessageBody class
# it provides message body abstration for Message
#
class MessageBody:
  def __init__(self, bodyType):
    """docstring for __init__"""
    self.bodyType = bodyType
    buildBody(bodyType)

  def buildBody(self):
    """Create header based on bodyType"""
    pass
