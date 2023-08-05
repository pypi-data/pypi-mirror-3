"""
Authors: www.iExpertos.com
   - Carlos Ble (www.carlosble.com)

License: Apache 2 (http://www.apache.org/licenses/LICENSE-2.0.html)

Project home: http://www.pydoubles.org
"""

from core import _CallsRepository_, _StubsRepository_
from core import _EmptyObject_, _Introspector_
from core import _DoubleMethodHandler_, _MirrorMethodHandler_, _RaiserMethodHandler_, _HardcodedMethodHandler_
from core import UnexpectedBehavior, WrongApiUsage, ApiMismatch
from core import ArgsDontMatch, ANY_ARG

class ProxySpy(object):
    """
    This test double is just an _interceptor to the original object.
    It watches the calls to the original, recording what happens
    so that we can make assertions on the calls that were made.
    The actual methods in the original object are executed, they
    are not mocked or stubbed by default.
    """
    def __init__(self, original_instance):
        self.calls = _CallsRepository_()
        self.introspector = _Introspector_()
        self.stubs = _StubsRepository_()
        self.original_instance = original_instance
        self.original_instance._double = self
        self.asserting_on_method = None
        self.invoked_method_name = None

    def __getattr__(self, attr):
        return _DoubleMethodHandler_(self, attr)
        
    def _before_method(self, args, kwargs):
        self._replace_possible_alias_method_name()
        self.calls.register_call(self.invoked_method_name, 
                                            *args, **kwargs)
        
    def __remove_interceptor_from_call_args(self, args):
        return args[1:]
    
    def _on_method_call(self, *args, **kwargs):
        args = self.__remove_interceptor_from_call_args(args)
        self._before_method(args, kwargs)
        if self.stubs.is_stub_for_this_input(self.invoked_method_name, args, kwargs):
           return self.stubs.return_value_given_input(
                         self.invoked_method_name, args, kwargs)
        return self._invoke_method(args, kwargs)
        
    def _invoke_method(self, args, kwargs):
        original_method = getattr(self.original_instance, self.invoked_method_name)
        return original_method(*args, **kwargs)
        
    def _was_called(self, method):
        return self._assert_called(
                 self.introspector.method_name(method))

    def _assert_called(self, method_name):
        self.expected_args = self.expected_kwargs = None
        if self.calls.was_registered(method_name):
           return self
        else:
           raise UnexpectedBehavior("The method was not called:" + method_name)

    def was_called(self):
        return self._assert_called(self._name_of_method_under_assertion())
        
    def was_never_called(self):
        if not self.calls.was_registered(self._name_of_method_under_assertion()):
           return self
        else:
           raise UnexpectedBehavior(
               "The method was called indeed:" +
               self._name_of_method_under_assertion())

    def _is_asserting_that_call_was_made(self):
        return self.asserting_on_method is not None
    
    def with_args(self, *args, **kwargs):
        if self._is_asserting_that_call_was_made():
           self.expected_args = args
           self.expected_kwargs = kwargs
           self.calls.assert_match_call(
               self._name_of_method_under_assertion(), *args, **kwargs)
        else:
           self.stubs.set_input_for_last_stubbed_method(args, kwargs)
        return self

    def times(self, times):
        self._assert_that_is_at_least_twice(times)
        if self.calls.was_registered(
                self._name_of_method_under_assertion(), times,
                self.expected_args, self.expected_kwargs):
           return self
        else:
            raise UnexpectedBehavior(
                "The method was not called %s times: %s" %
                (str(times), self._name_of_method_under_assertion()))

    def _assert_that_is_at_least_twice(self, times):
        if times <= 1:
            raise WrongApiUsage('Times cant be less than 2. For just one time, do not specify times. For zero times, use a spy with was_never_called')

    def _name_of_method_under_assertion(self):
        return self.introspector.method_name(self.asserting_on_method)

    def stub_out(self, method):
        self.stubs.create_stub(self.introspector.method_name(method))
        
    def then_return(self, args):
        self.stubs.set_output_for_last_stubbed_method(args)
        return self

    def then_raise(self, exception_instance):
        self.stubs.set_output_for_last_stubbed_method(method_raising(exception_instance))

    def then_return_input(self):
        self.stubs.set_output_for_last_stubbed_method(_MirrorMethodHandler_())
        
    def _replace_possible_alias_method_name(self):
        for method_name in self.stubs.stubbed_method_names():
            if self.introspector.are_synonymous(self.original_instance, 
                             self.invoked_method_name, method_name):
               self.invoked_method_name = method_name
               return
        
class Spy(ProxySpy):
    """
    Works like a ProxySpy but methods are stubbed returning
    nothing by default, rather than calling the doubled object.
    The spy will check if the API consumed by the user matches
    the actual API in the doubled object.
    """
    DEFAULT_RETURN_VALUE_FOR_STUBBED_METHOD = None
    
    def _api_mismatch_msg(self, original_args, args):
        return "The number of arguments in the actual object <%s> don't match the actual call on the double <%s>" % (
               str(tuple(original_args)).replace("'self', ", ""),
               str(args))
            
    def _was_called(self, method):
        method_name = self.introspector.method_name(method)
        if not hasattr(self.original_instance, method_name):  
           raise ApiMismatch('Object instance has no method %s' % method_name)
        return super(Spy, self)._was_called(method)
                    
    def _check_api_match(self, args, kwargs):
        original_method = getattr(self.original_instance, 
                                  self.invoked_method_name)
        args_plus_kwargs_spec_len, kwargs_spec_len, arg_spec = \
          self.introspector.original_method_signature(original_method)
        if len(args) + len(kwargs) != args_plus_kwargs_spec_len and \
           len(args) != args_plus_kwargs_spec_len - kwargs_spec_len:
             msg = self._api_mismatch_msg(arg_spec.args, args) 
             raise ApiMismatch(msg)
        
    def _is_not_an_empty_spy(self):
        return not hasattr(self.original_instance, "_empty_object__")

    def _before_method(self, args, kwargs):
        super(Spy, self)._before_method(args, kwargs)
        if self._is_not_an_empty_spy():
           self._check_api_match(args, kwargs)        
        
    def _invoke_method(self, args, kwargs):
        return self.DEFAULT_RETURN_VALUE_FOR_STUBBED_METHOD

class Mock(Spy):
    """
    Any method that is going to be invoked on this object must
    be expected through the expect_call method before invoking it. 
    Otherwise, an exception will be thrown. 
    """
    def __init__(self, obj_instance):
        super(Mock, self).__init__(obj_instance)
        self.satisfied_expectations = _StubsRepository_()
        
    def add_expectation(self, method):
        self.stub_out(method)
        
    def _before_method(self, args, kwargs):
        super(Mock, self)._before_method(args, kwargs)
        if self.stubs.is_stub_for_this_input(self.invoked_method_name, args, kwargs):
           self.satisfied_expectations.add_stub(self.invoked_method_name, args, kwargs)
        else:
           raise UnexpectedBehavior(
                 "\nThis call wasn't expected:\n  '%s[args=%s,kwargs=%s]' .\nExpected calls are:\n  %s" % (
                 self.invoked_method_name, 
                 str(args), str(kwargs),
                 self.stubs.show_all_methods()))
                          
    def returning(self, args):
        return super(Mock, self).then_return(args)
    
    def times(self, times):
        self._assert_that_is_at_least_twice(times)
        self.stubs.repeat_stub_times(times)
    
    def assert_expectations(self):
        self.assert_that_is_satisfied()
        
    def assert_that_is_satisfied(self):
        if not self.stubs.repositories_are_equivalent(
                    self.satisfied_expectations):
           raise UnexpectedBehavior(
                 "\nDefined expectations were not satisfied. \nRegistered calls are:\n   %s\nBut expectations are\n   %s" % (
                        self.calls.show_registered_calls(),
                        self.stubs.show_all_methods()))

# PUBLIC STATIC METHODS:
def proxy_spy(obj_instance):
    """
    Creates a spy objet that records the calls made but passes them
    to the actual object.
    """
    return ProxySpy(obj_instance)
        
def spy(obj_instance):
    """
    Creates a spy object based on the given object instance
    """
    return Spy(obj_instance)

def empty_stub():
    """
    Creates a stub object in which you can dynamically add any method  
    """
    return empty_spy()

def stub(obj_instance):
    """
    Creates a stub object based on the given object instance
    """
    return spy(obj_instance)

def empty_spy():
    """
    Creates a spy object but will not check any API match
    """
    return Spy(_EmptyObject_())

def mock(obj_instance):
    """
    Creates a mock objet based on the given object instance
    """
    return Mock(obj_instance)

def empty_mock():
    """
    Creates a mock objet but will not check any API match
    """
    return mock(_EmptyObject_())

def method_returning(return_value):
    """
    Creates a method stub, able to receive anything and return 
    the given return_value
    """
    return _HardcodedMethodHandler_(return_value)

def method_raising(exception_instance):
    """
    Creates a method stub, which raises the given exception
    """
    return _RaiserMethodHandler_(exception_instance)    
    
def expect_call(method):
    """
    Define behavior in a mock object
    """
    double = _Introspector_().double_instance_from_method(method)
    double.add_expectation(method)
    return double
    
def when(method):
    """
    Define behavior in a stub or spy object
    """
    double = _Introspector_().double_instance_from_method(method)
    double.stub_out(method)
    return double  
        
def assert_that_was_called(method):
    """
    Verify the behavior in a spy. Use this with spies only.
    For mock objects use: mock_instance.assert_that_is_satisfied() 
    """
    try:
        double = _Introspector_().double_instance_from_method(method) 
        double.asserting_on_method = method
        return double._was_called(method)
    except AttributeError, e:
        raise WrongApiUsage(
            "Make sure you call assert, passing in a method from a test double: (double.method)")
        
def assert_that_method(method):
    """
    Alternative to assert_that_was_called:
    assert_that(obj.method).was_called() 
    """
    double = _Introspector_().double_instance_from_method(method) 
    double.asserting_on_method = method
    return double