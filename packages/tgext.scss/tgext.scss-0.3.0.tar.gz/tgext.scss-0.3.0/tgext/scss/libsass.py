from ctypes import *
import ctypes.util

import sys, copy

ENCODING = 'utf-8'
if sys.version_info[0] == 3:
    to_char_array = lambda s: bytes(s, ENCODING)
    to_string = lambda x: x.decode(ENCODING)
    EMPTY_STRING = bytes()
else:
    to_char_array = lambda x: x
    to_string = lambda x: x
    EMPTY_STRING = ""

LIB_PATH = ctypes.util.find_library("sass")

if LIB_PATH is None:
    raise LookupError("couldn't find path to libsass")

LIB = cdll.LoadLibrary(LIB_PATH)

class Style():
    NESTED     = 0
    EXPANDED   = 1
    COMPACT    = 2
    COMPRESSED = 3

class Options(Structure):
    """
    struct sass_options {
      int output_style;
      char* include_paths;
    };
    """

    def __init__(self, output_style=Style.NESTED, include_paths=""):
        self.output_style = output_style
        self.include_paths = to_char_array(include_paths)

    _fields_ = [
        ("output_style", c_int),
        ("include_paths", c_char_p)
    ]

class Context(Structure):
    """
    struct sass_context {
      char* source_string;
      char* output_string;
      struct sass_options options;
      int error_status;
      char* error_message;
    };
    """

    _fields_ = [
        ("source_string", c_char_p),
        ("output_string", c_char_p),
        ("options", Options),
        ("error_status", c_int),
        ("error_message", c_char_p)
    ]

    def init(self, source_string=""):
        self.source_string = to_char_array(source_string)
        self.output_string = EMPTY_STRING
        self.options = Options()
        self.error_status = 0
        self.error_message = EMPTY_STRING

    def __str__(self):
        return '<context source="{source_string} output="{output_string}" status="{error_status}" error="{error_message}>"'.format(
            source_string=self.source_string,
            output_string=self.output_string,
            error_status=self.error_status,
            error_message=self.error_message)

_new_context = LIB.sass_new_context
_new_context.argtypes = []
_new_context.restype = Context

_compile = LIB.sass_compile
_compile.restype = c_int
_compile.argtypes = [POINTER(Context)]

def compile(scss, include_paths):
    ctx = _new_context()
    ctx.init(scss)
    ctx.options = Options(Style.NESTED, include_paths)

    _compile(ctx)

    if ctx.error_status:
        result = ctx.error_message
        return False, result
    else:
        result = ctx.output_string
        return True, result



