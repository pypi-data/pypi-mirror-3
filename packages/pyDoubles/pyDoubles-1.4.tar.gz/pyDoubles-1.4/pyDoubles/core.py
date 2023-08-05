"""
Authors: www.iExpertos.com
   - Carlos Ble (www.carlosble.com)

License: Apache 2 (http://www.apache.org/licenses/LICENSE-2.0.html)

Project home: http://www.pydoubles.org
"""

import inspect
import safeunicode
import unittest

ANY_ARG = "<___ANY___ARG___>"

_FailureException = unittest.TestCase.failureException

class UnexpectedBehavior(_FailureException):
    pass

class WrongApiUsage(_FailureException):
    pass

class ArgsDontMatch(_FailureException):
    pass

class ApiMismatch(_FailureException):
    pass

class _MatchFinder_():
    def args_dont_match(self, arg1, arg2):
        return not self._args_match(arg1, arg2)

    def _args_match(self, arg1, arg2):
        if self._are_valid_args(arg1, arg2):    
            if self._is_a_matcher_object(arg1):
                return self._matches(arg1, arg2)
            if self._is_a_matcher_object(arg2):
                return self._matches(arg2, arg1)
        return False

    def _are_valid_args(self, arg1, arg2):
        return arg1 is not None and arg2 is not None

    def _is_a_matcher_object(self, arg):
        return callable(self._get_match_method(arg))

    def _get_match_method(self, arg):
        return getattr(arg, "matches", None)
    
    def _matches(self, arg1, arg2):
        match_method = self._get_match_method(arg1)
        return match_method(arg2)
    
class _MethodHandler_(object):
    """
    Internal framework class. When user access a method or
    any other property in the test double, the framework
    return an instance of this class, which is callable.
    So calling this instance with parenthesis triggers
    the on_method_call event in the test double.
    """
    def callable_action(self, args, kwargs):
        pass
        
    def __call__(self, *args, **kwargs):
        return self.callable_action(args, kwargs)

class _DoubleMethodHandler_(_MethodHandler_):
    def __init__(self, double, attr):
        self.double = double
        self.attr_name = attr

    def callable_action(self, args, kwargs):
        self.double.invoked_method_name = self.attr_name
        return self.double._on_method_call(self, *args, 
                                                  **kwargs)                

class _HardcodedMethodHandler_(_MethodHandler_):
    def __init__(self, ret_val):
        self.ret_val = ret_val

    def callable_action(self, args, kwargs):
        return self.ret_val                

class _MirrorMethodHandler_(_MethodHandler_):
    def callable_action(self, args, kwargs):
        return args[0]           

class _RaiserMethodHandler_(_MethodHandler_):
    def __init__(self, exception):
        self.exception = exception

    def callable_action(self, args, kwargs):
        raise self.exception         

class _Introspector_():
    """
    Internal framework class. Specialized in introspection (reflection)
    """    
    def method_name(self, interceptor):
        return interceptor.attr_name
    
    def double_instance_from_method(self, interceptor):
        try:
            return interceptor.double
        except AttributeError,e:
            raise WrongApiUsage("Make sure you call this framework method passing in a method from a spy or a mock object")
    
    def original_method_signature(self, original_method):
        self_arg = 1
        arg_spec = inspect.getargspec(original_method)
        kargs_spec_len = 0
        args_plus_kwargs_spec_len = len(arg_spec.args) - self_arg 
        if arg_spec.defaults is not None:
           kargs_spec_len = len(arg_spec.defaults)
        return (args_plus_kwargs_spec_len, kargs_spec_len, arg_spec)
    
    def are_synonymous(self, instance, method_name1, method_name2):
        return getattr(instance, 
                       method_name1) == getattr(instance, 
                                                method_name2)

class _IOParams_():
    """
    Data structure class. Keeps method input and output
    """
    args = kwargs = output = None
    
    def set_output(self, output):
        self.output = output
        
    def is_stub_ignoring_args(self):
        return self.args is None and self.kwargs is None
                    
    def no_matter_input(self):
        return self.args is None and self.kwargs is None and \
               self.output is not None
    
    def __str__(self):
        return "args=%s,kwargs=%s,output=%s" % (str(self.args),
                                      str(self.kwargs), str(self.output))
    
class _MethodPool_(object):
    """
    Internal framework class. Intended to store methods info:
    The method name, the input arguments and the output for that
    input.
    """
    def __init__(self):
        self.pool = {}
        self.match_finder = _MatchFinder_()
    
    def _are_different_arguments(self, arg1, arg2):
        return arg1 != arg2 and \
               arg1 != ANY_ARG and \
               arg2 != ANY_ARG
            
    def _every_arg_matches_or_is_any_arg(self, args, last_call_args):
        for i in range(0, len(args)):
            defined_arg = args[i]
            received_arg = last_call_args[i]
            if self._are_different_arguments(defined_arg, received_arg):
               if self.match_finder.args_dont_match(defined_arg, received_arg):
                  return False
        return True
    
    def _do_args_tuple_match(self, args, last_call_args):
        if len(args) != len(last_call_args):
            return False
        return self._every_arg_matches_or_is_any_arg(args, last_call_args)
                   
    def _do_args_match(self, last_call_args, ioparams):
        if ioparams.args is not None and last_call_args is not None:
           return self._do_args_tuple_match(ioparams.args, last_call_args)
        return ioparams.args  == last_call_args

            
    def _do_kwargs_match(self, kwargs, ioparams):
        if ioparams.kwargs is not None:
           return kwargs == ioparams.kwargs
        else:
           return True
                         
    def __not_all_ioparams_match(self, called_collection, 
                                   local_collection):
        if len(called_collection) != len(local_collection):
            return True
        for i in range(0, len(local_collection)):
            if not self._do_args_match(called_collection[i].args, 
                                       local_collection[i]):
               if local_collection[i].args is not None:
                  return True
        return False
                        
    def do_pools_match(self, called_method_pool):
        for name, ioparams in self.pool.iteritems():
            if not called_method_pool.has_method(name) or \
               self.__not_all_ioparams_match(
                          called_method_pool.pool[name], ioparams):
               return False
        return True                

    def add_method(self, method_name, input_args=None, 
                   input_kwargs=None, output=None):
        if not self.pool.has_key(method_name):
            self.pool[method_name] = []
        ioparams = _IOParams_()
        ioparams.args = input_args
        ioparams.kwargs = input_kwargs
        ioparams.set_output(output)
        self.pool[method_name].append(ioparams)
        
    def has_method(self, method_name):
        return self.pool.has_key(method_name)

    def times_called(self, method_name, expected_args=None, expected_kwargs=None):
        return len(self.matching_ioparams_by_args(expected_args, expected_kwargs, method_name))
    
    def __expected_args_match(self, actual_ioparams, expected_args):
        if expected_args is None:
           return True
        else:
           return self._do_args_match(expected_args, actual_ioparams)
            
    def __expected_kwargs_match(self, actual_ioparams, expected_kwargs):
        if expected_kwargs is None:
           return True
        else:
           return self._do_kwargs_match(expected_kwargs, actual_ioparams)
            
    def matching_ioparams_by_args(self, expected_args, expected_kwargs, method_name):
        matching_ioparams = []
        for ioparams in self.pool[method_name]:
            if self.__expected_args_match(ioparams,expected_args) and \
               self.__expected_kwargs_match(ioparams, expected_kwargs):
                 matching_ioparams.append(ioparams)                
        return matching_ioparams    

    def stubbed_method_names(self):
        return self.pool.keys()
        
        
class _StubPool_(_MethodPool_):

    def matching_ioparams_by_args(self, call_args, call_kwargs, method_name):
        matching_ioparams = self._exact_matching_ioparams_by_args(call_args, call_kwargs, method_name)
        for ioparams in self.pool[method_name]:
            if ioparams.is_stub_ignoring_args():
               matching_ioparams.append(ioparams)
        return matching_ioparams
    
    def _exact_matching_ioparams_by_args(self, call_args, call_kwargs, method_name):
        matching_ioparams = []
        for ioparams in self.pool[method_name]:
            if self._do_args_match(call_args, ioparams) and \
               self._do_kwargs_match(call_kwargs, ioparams):
                  matching_ioparams.append(ioparams)
        return matching_ioparams
    
    def _ioparams_for_unspecified_method_input(self, method_name):
        for ioparams in self.pool[method_name]:
            if ioparams.no_matter_input():
               return ioparams
        return None

    def clone_last_ioparams(self, method_name):
        self.pool[method_name].append(self.pool[method_name][-1])
        
    def input_wasnt_specified(self, method_name):
        return self._ioparams_for_unspecified_method_input(
                            method_name) is not None    
                    
    def get_output_for_unspecified_method_input(self, method_name):
        ioparams = self._ioparams_for_unspecified_method_input(
                                            method_name)
        if ioparams is not None:
            return ioparams.output

    def get_output_for_specified_method_input(self, args, kwargs, method_name):
        matching_ioparams = self.matching_ioparams_by_args(args, kwargs, method_name)
        if len(matching_ioparams) > 0:
           return matching_ioparams[0].output
        
             
    def set_output_for_last_added_method(self, method_name, output):       
        ioparams = self.pool[method_name][-1]
        ioparams.set_output(output)
        self.pool[method_name][-1] = ioparams        
        
    def set_input_for_last_stubbed_method(self, method_name, 
                                          input_args=None,
                                          input_kwargs=None):
        ioparams = self.pool[method_name][-1]
        ioparams.args = input_args
        ioparams.kwargs = input_kwargs
        self.pool[method_name][-1] = ioparams


class _PoolReport_():
    """
    Displays the information stored in a MethodPool
    """
    def __init__(self, method_pool):
        self.methods_pool = method_pool
        
    def method_info(self, method_name):
        return ["(" + str(ioparams) + ")" for ioparams in self.methods_pool.pool[method_name]]
    
    def all_stored_methods(self):
        info = ""
        for key in self.methods_pool.pool:
            info = "%s%s, %s" % (key, str(self.method_info(key)), info)
        if len(info) == 0:
            return "No one"
        return info

class _CallsRepository_():
    """
    Internal framework class. Basically a wrapper around
    the MethodPool, to store calls to methods
    """    
    def __init__(self):
        self.method_pool = _MethodPool_()
        self.report = _PoolReport_(self.method_pool)
        
    def register_call(self, method_name, *args, **kwargs):
        self.method_pool.add_method(method_name, 
                                    input_args=args,
                                    input_kwargs=kwargs)
         
    def was_registered(self, method_name, times=None, args=None, kwargs=None):
        if times == None:
            return self.method_pool.has_method(method_name)
        else:
            return self.method_pool.times_called(method_name, args, kwargs) == times

    def _readable_kwargs(self, kwargs_str):
        if kwargs_str == "{}":
            return "No keyword args where passed in"
        return kwargs_str
      
    def _format_err_msg(self, method_name, args, kwargs):
        args_str = ",".join([str(safeunicode.get_string(arg)) for arg in args])
        kwargs_str = ",".join([str(safeunicode.get_string(kwarg)) for kwarg in kwargs])
        return "RECORDED calls were: << %s >>, \n EXPECTED call is << (args = %s), (keyword args = %s) >>" % (
                str(self.report.method_info(method_name)), 
                args_str, self._readable_kwargs(kwargs_str))

    def _some_call_matches_this_assertion(self, expected_args, expected_kwargs, method_name):
        matching_ioparams = self.method_pool.matching_ioparams_by_args(expected_args, expected_kwargs, method_name)
        return len(matching_ioparams) > 0

    def assert_match_call(self, method_name, *args, **kwargs):
        if not self._some_call_matches_this_assertion(
                        args, kwargs, method_name):
                raise ArgsDontMatch(self._format_err_msg(
                         method_name, args, kwargs))
                
    def show_registered_calls(self):
        return self.report.all_stored_methods()
        
class _StubsRepository_():
    """
    Internal framework class. Pretty much a wrapper
    around the StubPool class, to store stubs
    """
    UNDEFINED = "undefined_____"
    
    def __init__(self):
        self.method_pool = _StubPool_()
        self.report = _PoolReport_(self.method_pool)
        self._clear_stub_definition()

    def _clear_stub_definition(self):
        self.last_stubbed_method = None
            
    def will_stub_any_input(self):
        return self._is_stub_for_any_input(self.last_stubbed_method)
               
    def _some_stub_matches_this_call(self, call_args, call_kwargs, method_name):
        matching_ioparams = self.method_pool.matching_ioparams_by_args(call_args, call_kwargs, method_name)
        return len(matching_ioparams) > 0
      
    def is_stub_for_this_input(self, method_name, args, kwargs):
        return self.method_pool.has_method(method_name) and \
               self._some_stub_matches_this_call(args, kwargs, method_name)            
             
    def _is_stub_for_any_input(self, method_name):
        return self.method_pool.has_method(method_name) and \
               self.method_pool.input_wasnt_specified(method_name)
            
    def return_value_given_input(self, method_name, args, kwargs):
        if self.is_stub_for_this_input(method_name, args, kwargs):
           output = self.method_pool.get_output_for_specified_method_input(args, kwargs, method_name)           
        else:
           if self._is_stub_for_any_input(method_name):
              output = self.method_pool.get_output_for_unspecified_method_input(method_name)
        if isinstance(output, _MethodHandler_):
           return self._execute_output_method(output, method_name, args, kwargs)
        return output

    def _execute_output_method(self, method, name, args, kwargs):
        try:
           return method(*args, **kwargs)
        except IndexError:
           raise ApiMismatch(
                "Method %s seems to require arguments but haven't been passed in" % (
                        name,))
                      
    def add_stub(self, method_name, args, kwargs):
        self.create_stub(method_name)
        self.set_input_for_last_stubbed_method(args, kwargs)

    def create_stub(self, method_name):
        self._clear_stub_definition()
        self.last_input_args = self.last_input_kwargs = None
        self.last_stubbed_method = method_name
        self.method_pool.add_method(method_name)
        
    def set_input_for_last_stubbed_method(self, args, kwargs):
        self.last_input_args = args
        self.last_input_kwargs = kwargs
        self.method_pool.set_input_for_last_stubbed_method(
                                    self.last_stubbed_method, 
                                    input_args=args,
                                    input_kwargs=kwargs)
        
    def repeat_stub_times(self, times):
        for i in range(0, times -1):
            self.method_pool.clone_last_ioparams(self.last_stubbed_method)
                
    def set_output_for_any_input_in_last_stubbed_method(self, output):
        self.method_pool.add_method(self.last_stubbed_method, 
                                    output=output)
                    
    def set_output_for_last_stubbed_method(self, output):
        self.method_pool.set_output_for_last_added_method(self.last_stubbed_method, output)
                                            
    def show_all_methods(self):
        return self.report.all_stored_methods()
                
    def repositories_are_equivalent(self, repository):
        return self.method_pool.do_pools_match(repository.method_pool)
                
    def stubbed_method_names(self):
        return self.method_pool.stubbed_method_names()
                
class _EmptyObject_():
    """
    Internal framework class. Intended to be used as the original_object
    for empty_spy and empty_mock
    """
    asserting_on_method = None
    _empty_object__ = True
    def method(self, *args, **kwargs):
        pass
    
    def __getattr__(self, attr):
        return attr