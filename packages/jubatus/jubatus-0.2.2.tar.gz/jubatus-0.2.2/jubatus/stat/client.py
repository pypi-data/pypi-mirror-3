
import msgpackrpc
from types import *


class stat:
  def __init__ (self, host, port):
    address = msgpackrpc.Address(host, port)
    self.client = msgpackrpc.Client(address)

  def set_config (self, name, c):
    retval = self.client.call('set_config', name, c)
    return retval

  def get_config (self, name):
    retval = self.client.call('get_config', name)
    return config_data.from_msgpack(retval)

  def push (self, arg0, arg1, arg2):
    retval = self.client.call('push', arg0, arg1, arg2)
    return retval

  def sum (self, arg0, arg1):
    retval = self.client.call('sum', arg0, arg1)
    return retval

  def stddev (self, arg0, arg1):
    retval = self.client.call('stddev', arg0, arg1)
    return retval

  def max (self, arg0, arg1):
    retval = self.client.call('max', arg0, arg1)
    return retval

  def min (self, arg0, arg1):
    retval = self.client.call('min', arg0, arg1)
    return retval

  def entropy (self, arg0, arg1):
    retval = self.client.call('entropy', arg0, arg1)
    return retval

  def moment (self, arg0, arg1, n, c):
    retval = self.client.call('moment', arg0, arg1, n, c)
    return retval

  def save (self, name, arg1):
    retval = self.client.call('save', name, arg1)
    return retval

  def load (self, name, arg1):
    retval = self.client.call('load', name, arg1)
    return retval

  def get_status (self, name):
    retval = self.client.call('get_status', name)
    return {k_retval : {k_v_retval : v_v_retval for k_v_retval,v_v_retval in v_retval.items()} for k_retval,v_retval in retval.items()}


