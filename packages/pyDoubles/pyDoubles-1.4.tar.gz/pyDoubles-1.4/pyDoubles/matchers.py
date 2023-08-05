"""
Authors:
    Carlos Ble (www.carlosble.com)
    Ruben Bernardez (www.rubenbp.com)
    www.iExpertos.com
License: Apache 2 (http://www.apache.org/licenses/LICENSE-2.0.html)
Project home: https://bitbucket.org/carlosble/pydoubles
"""

import safeunicode
import re
from core import WrongApiUsage

# PUBLIC API
def str_containing(substr):
    return _SubstrMatcher_(substr)

def str_not_containing(substr):
    return _NotSubstrMatcher_(substr)

def str_length(arg):
    return _LengthMatcher_(arg)

def obj_with_fields(arg):
    return _ObjWithFieldsMatcher_(arg)

# CORE API
class PyDoublesMatcher(object):
    matcher_name = "pyDoublesMatcher"

    def __str__(self):
        try:
            return self.matcher_name + " '" + str(safeunicode.get_string(self.defined_arg)) + "'"
        except:
            return str(self.__class__)
        
    def matches(self, received_arg):
        return False

class _LengthMatcher_(PyDoublesMatcher):
    matcher_name = "string with length"    

    def __init__(self, length):
        self.defined_arg = length
    
    def matches(self, text):
        return int(self.defined_arg) == len(text)

class _SubstrMatcher_(PyDoublesMatcher):
    matcher_name = "string containing"  
          
    def __init__(self, substring):
        self.defined_arg = self.__prepare_arg(substring)
    
    def __prepare_arg(self, substring):
        return safeunicode.get_string(substring)
        
    def matches(self, arg2):
        try:
            self.arg2 = self.__prepare_arg(arg2)
            return self._comparison()
        except TypeError:
            return False

    def _comparison(self):
        return re.search(self.defined_arg, self.arg2)

class _NotSubstrMatcher_(_SubstrMatcher_):
    matcher_name = "string NOT containing"     

    def __init__(self, substring):
        super(_NotSubstrMatcher_, self).__init__(substring)

    def _comparison(self):
        return not re.search(self.defined_arg, self.arg2)

class _ObjWithFieldsMatcher_(PyDoublesMatcher):
    matcher_name = "Object with certain value in the field"    

    def __init__(self, field_dict):
        if not hasattr(field_dict, "iteritems"):
            raise WrongApiUsage("This matcher requires a dictionary: {'name': value} ")
        self.defined_arg = field_dict
    
    def matches(self, arg):
        for field_name, field_value in self.defined_arg.iteritems():
            if getattr(arg, field_name) != field_value:
                return False
        return True
        
