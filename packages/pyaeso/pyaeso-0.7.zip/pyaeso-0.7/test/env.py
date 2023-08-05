import os
from tempfile import mkdtemp
from os.path import (
    join,
    dirname,
)

__test_dir = dirname(__file__)

def res_dir():
    return join(__test_dir, 'res')

try:
    __log_dir = os.environ['PYAESO_LOG_DIR']
except KeyError:
    __log_dir = mkdtemp(prefix = 'pyaeso')

def log_dir():
    return __log_dir
