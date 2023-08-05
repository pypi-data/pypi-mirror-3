# -*- coding: utf-8 -*-
import os
from ctypes import *
from ctypes.util import find_library

import stdc

__all__ = [
    'SENSORS_LIB', 'VERSION', 'MAJOR_VERSION', 'SensorsError', '_error_check',
    'init', 'cleanup'
]

LIB_FILENAME = os.environ.get('SENSORS_LIB') or find_library('sensors')
SENSORS_LIB = CDLL(LIB_FILENAME)
VERSION = c_char_p.in_dll(SENSORS_LIB, 'libsensors_version').value
MAJOR_VERSION = int(VERSION.split('.', 1)[0])


class SensorsError(Exception):
    def __init__(self, message, error_number=None):
        Exception.__init__(self, message)
        self.error_number = error_number


def _error_check(result, _func, _arguments):
    if result < 0:
        raise SensorsError(_strerror(result), result)

_strerror = SENSORS_LIB.sensors_strerror
_strerror.argtypes = [c_int]
_strerror.restype = c_char_p

_init = SENSORS_LIB.sensors_init
_init.argtypes = [c_void_p]
_init.restype = c_int
_init.errcheck = _error_check

cleanup = SENSORS_LIB.sensors_cleanup
cleanup.argtypes = None
cleanup.restype = None


def init(config_filename=None):
    if config_filename is None:
        config_filename = DEFAULT_CONFIG_FILENAME
    file_p = stdc.fopen(config_filename, 'r')
    if file_p is None:
        error_number = get_errno()
        raise OSError(error_number, os.strerror(error_number), config_filename)
    try:
        _init(file_p)
    finally:
        stdc.fclose(file_p)
