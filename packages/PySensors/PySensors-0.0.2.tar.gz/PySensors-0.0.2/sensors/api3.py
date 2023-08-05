#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ctypes import *

import common
import stdc
from common import *

__all__ = ['API_VERSION', 'DEFAULT_CONFIG_FILENAME', 'iter_detected_chips']

API_VERSION = 3
common.DEFAULT_CONFIG_FILENAME = DEFAULT_CONFIG_FILENAME = '/etc/sensors.conf'


class Feature(Structure):
    _fields_ = [
        ('number', c_int),
        ('name', c_char_p),
        ('mapping', c_int),
        ('compute_mapping', c_int),
        ('mode', c_int),
    ]
    
    NO_MAPPING = -1
    
    def __repr__(self):
        return '<%s number=%d name=%r mapping=%d compute_mapping=%d mode=%d' % (
            self.__class__.__name__,
            self.number,
            self.name,
            self.mapping,
            self.compute_mapping,
            self.mode
        )
    
    def __iter__(self):
        return self.chip._iter_features(self.number)
    
    @property
    def label(self):
        result_p = c_char_p()
        _get_label(self.chip, self.number, byref(result_p))
        result = result_p.value
        stdc.free(result_p)
        return result
    
    def get_value(self):
        result = c_double()
        _get_feature(self.chip, self.number, byref(result))
        return result.value

FEATURE_P = POINTER(Feature)


class Chip(Structure):
    # 
    # TODO Implement a `__str__()` method.
    # TODO Move common stuff into `AbstractChip` class.
    # 
    _fields_ = [
        ('prefix', c_char_p),
        ('bus', c_int),
        ('addr', c_int),
        ('busname', c_char_p),
    ]
    
    def __new__(cls, *args):
        result = super(Chip, cls).__new__(cls)
        if args:
            _parse_chip_name(args[0], byref(result))
        return result
    
    def __init__(self, *_args):
        Structure.__init__(self)
    
    def __repr__(self):
        return '<%s prefix=%r bus=%r addr=%r busname=%r>' % (
            (
                self.__class__.__name__,
                self.prefix,
                self.bus,
                self.addr,
                self.busname
            )
        )
    
    def __iter__(self):
        return self._iter_features()
    
    @property
    def has_wildcards(self):
        return bool(_chip_name_has_wildcards(self))
    
    @property
    def adapter_name(self):
        return _get_adapter_name(self.bus)
    
    def match(self, other):
        return bool(_match_chip(self, other))
    
    def _iter_features(self, parent=Feature.NO_MAPPING):
        nr1, nr2 = c_int(0), c_int(0)
        while True:
            result_p = _get_all_features(self, byref(nr1), byref(nr2))
            if not result_p:
                break
            result = result_p.contents
            if result.mapping == parent:
                result.chip = self
                result.subfeatures = dict()
                yield result

CHIP_P = POINTER(Chip)


# 
# TODO Implement a handler for at least `sensors_parse_error`.
# 

_parse_chip_name = SENSORS_LIB.sensors_parse_chip_name
_parse_chip_name.argtypes = [c_char_p, CHIP_P]
_parse_chip_name.restype = c_int
_parse_chip_name.errcheck = _error_check

_match_chip = SENSORS_LIB.sensors_match_chip
_match_chip.argtypes = [Chip, Chip]
_match_chip.restype = c_int

_chip_name_has_wildcards = SENSORS_LIB.sensors_chip_name_has_wildcards
_chip_name_has_wildcards.argtypes = [Chip]
_chip_name_has_wildcards.restype = c_int

_get_adapter_name = SENSORS_LIB.sensors_get_adapter_name
_get_adapter_name.argtypes = [c_int]
_get_adapter_name.restype = c_char_p

_get_label = SENSORS_LIB.sensors_get_label
_get_label.argtypes = [Chip, c_int, POINTER(c_char_p)]
_get_label.restype = c_int
_parse_chip_name.errcheck = _error_check

# 
# TODO sensors_get_ignored()
# 

_get_feature = SENSORS_LIB.sensors_get_feature
_get_feature.argtypes = [Chip, c_int, POINTER(c_double)]
_get_feature.restype = c_int
_parse_chip_name.errcheck = _error_check

# 
# TODO sensors_set_feature()
# TODO sensors_do_chip_sets()
# TODO sensors_do_all_sets()    (common function)
# 

_get_detected_chips = SENSORS_LIB.sensors_get_detected_chips
_get_detected_chips.argtypes = [POINTER(c_int)]
_get_detected_chips.restype = CHIP_P

_get_all_features = SENSORS_LIB.sensors_get_all_features
_get_all_features.argtypes = [Chip, POINTER(c_int), POINTER(c_int)]
_get_all_features.restype = FEATURE_P


def iter_detected_chips(chip_name='*-*'):
    chip = Chip(chip_name)
    number = c_int(0)
    while True:
        result_p = _get_detected_chips(byref(number))
        if not result_p:
            break
        result = result_p.contents
        # 
        # TODO Add ignore check.
        # 
        if chip.match(result):
            yield result
