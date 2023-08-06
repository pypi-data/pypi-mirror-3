
# This file is auto-generated from src/server/classifier.idl
# *** DO NOT EDIT ***


import sys
import msgpack


class param_t:
  @staticmethod
  def from_msgpack(arg):
    return {k_arg : v_arg for k_arg,v_arg in arg.items()}

class string_rule:
  def __init__(self, key, t, sample_weight, global_weight):
    self.key = key
    self.t = t
    self.sample_weight = sample_weight
    self.global_weight = global_weight

  def to_msgpack(self):
    return (
      self.key,
      self.t,
      self.sample_weight,
      self.global_weight,
      )

  @staticmethod
  def from_msgpack(arg):
    return string_rule(
      arg[0],
      arg[1],
      arg[2],
      arg[3])

class filter_rule:
  def __init__(self, key, t, suffix):
    self.key = key
    self.t = t
    self.suffix = suffix

  def to_msgpack(self):
    return (
      self.key,
      self.t,
      self.suffix,
      )

  @staticmethod
  def from_msgpack(arg):
    return filter_rule(
      arg[0],
      arg[1],
      arg[2])

class num_rule:
  def __init__(self, key, t):
    self.key = key
    self.t = t

  def to_msgpack(self):
    return (
      self.key,
      self.t,
      )

  @staticmethod
  def from_msgpack(arg):
    return num_rule(
      arg[0],
      arg[1])

class converter_config:
  def __init__(self, string_filter_types, string_filter_rules, num_filter_types, num_filter_rules, string_types, string_rules, num_types, num_rules):
    self.string_filter_types = string_filter_types
    self.string_filter_rules = string_filter_rules
    self.num_filter_types = num_filter_types
    self.num_filter_rules = num_filter_rules
    self.string_types = string_types
    self.string_rules = string_rules
    self.num_types = num_types
    self.num_rules = num_rules

  def to_msgpack(self):
    return (
      self.string_filter_types,
      self.string_filter_rules,
      self.num_filter_types,
      self.num_filter_rules,
      self.string_types,
      self.string_rules,
      self.num_types,
      self.num_rules,
      )

  @staticmethod
  def from_msgpack(arg):
    return converter_config(
      {k_arg_0_ : param_t.from_msgpack(v_arg_0_) for k_arg_0_,v_arg_0_ in arg[0].items()},
      [filter_rule.from_msgpack(elem_arg_1_) for elem_arg_1_ in arg[1]],
      {k_arg_2_ : param_t.from_msgpack(v_arg_2_) for k_arg_2_,v_arg_2_ in arg[2].items()},
      [filter_rule.from_msgpack(elem_arg_3_) for elem_arg_3_ in arg[3]],
      {k_arg_4_ : param_t.from_msgpack(v_arg_4_) for k_arg_4_,v_arg_4_ in arg[4].items()},
      [string_rule.from_msgpack(elem_arg_5_) for elem_arg_5_ in arg[5]],
      {k_arg_6_ : param_t.from_msgpack(v_arg_6_) for k_arg_6_,v_arg_6_ in arg[6].items()},
      [num_rule.from_msgpack(elem_arg_7_) for elem_arg_7_ in arg[7]])

class config_data:
  def __init__(self, method, config):
    self.method = method
    self.config = config

  def to_msgpack(self):
    return (
      self.method,
      self.config,
      )

  @staticmethod
  def from_msgpack(arg):
    return config_data(
      arg[0],
      converter_config.from_msgpack(arg[1]))

class datum:
  def __init__(self, sv, nv):
    self.sv = sv
    self.nv = nv

  def to_msgpack(self):
    return (
      self.sv,
      self.nv,
      )

  @staticmethod
  def from_msgpack(arg):
    return datum(
      [ (elem_arg_0_[0], elem_arg_0_[1], )  for elem_arg_0_ in arg[0]],
      [ (elem_arg_1_[0], elem_arg_1_[1], )  for elem_arg_1_ in arg[1]])

class estimate_result:
  def __init__(self, label, prob):
    self.label = label
    self.prob = prob

  def to_msgpack(self):
    return (
      self.label,
      self.prob,
      )

  @staticmethod
  def from_msgpack(arg):
    return estimate_result(
      arg[0],
      arg[1])


