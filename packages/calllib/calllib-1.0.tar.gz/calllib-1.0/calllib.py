########################################################################
# A library for calling callables with runtime-defined parameters.
#
# Copyright 2005-2011 True Blade Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Notes:
#  Uses the inspect module to compute actual function arguments.
########################################################################

import inspect as _inspect
import types as _types

__all__ = ['apply', 'getargs']

class ArgumentError(Exception): pass

def _get_arg(args_dict, arg_name, arg_num, n_args, defaults):
    try:
        # look this up in the dictionary of arguments, if it's present
        return args_dict[arg_name]
    except KeyError:
        pass

    # not in the dictionary, see if a default exists for this argument
    try:
        return defaults[arg_num - n_args]
    except (IndexError, TypeError):
        # TypeError if defaults is None
        # IndexError if no default for this argument
        raise ValueError('no value and no default for %r' % arg_name)


def _get_callable_info(fn):
    # return a list of argument_names, and a list of default values
    original_type = type(fn)

    # see if this is really an object with a __call__ method
    if type(fn) == _types.InstanceType:
        fn = fn.__call__

    # if this is a new or old stype class, look at the __init__ method
    if type(fn) == _types.ClassType:
        # old style function
        nskip = 1
        try:
            fn = fn.__init__
        except AttributeError:
            # no __init__, so this can be called with
            #  no params
            return [], []

    elif type(fn) == _types.TypeType:
        # new style
        # there's always an __init__ function, for object
        nskip = 1
        fn = fn.__init__

        # can't inspect object.__init__, so just say it has
        #  no params and no defaults
        if fn is object.__init__:
            return [], []

    elif type(fn) == _types.FunctionType:
        nskip = 0
    elif type(fn) == _types.MethodType:
        # bound method?
        if fn.im_self is None:
            nskip = 0
        else:
            nskip = 1
    else:
        raise TypeError('calllib unsupported type %r' % fn)

    # inspect the ultimate callable
    argspec = _inspect.getargspec(fn)
    return argspec.args[nskip:], argspec.defaults


def getargs(callable, args):
    '''Given a callable object `callable`, and a mapping of arguments
       `args`, return a list of arguments for the callable. Handles
       default arguments that are not in args.'''

    arg_names, defaults = _get_callable_info(callable)

    return [_get_arg(args, arg_name, n, len(arg_names), defaults)
            for n, arg_name in enumerate(arg_names)]


def apply(callable, args):
    '''Given a callable object `callable`, and a mapping of arguments
       `args`, call `callable` with arguments taken from `args`. The
       arguments are found by matching argument names from the values
       in `args`.'''

    return callable(*getargs(callable, args))


if __name__ == '__main__':
    import unittest

    class OkException(Exception): pass

    class TestCase(unittest.TestCase):

        def test_free_function(self):
            def fn(foo, bar):
                if foo == 'foo' and bar == 'bar':
                    raise OkException()

            self.assertRaises(OkException, apply, fn, {'foo':'foo', 'bar':'bar'})


        def test_free_function_with_defaults(self):
            def fn(foo, foo1='foo1', bar='notbar', baz='baz'):
                if foo == 'foo' and foo1 == 'foo1' and bar == 'bar' and baz == 'baz':
                    raise OkException()

            self.assertRaises(OkException, apply, fn, {'foo':'foo', 'bar':'bar'})


        def test_free_function_with_missing_args(self):
            def fn(foo):
                pass

            self.assertRaises(ValueError, apply, fn, {})


        def test_return_value(self):
            def fn(x, y=10):
                return x+y
            self.assertEqual(apply(fn, {'x': 32}), 42)


        def test_bound_method(self):
            class C:
                def __init__(self):
                    self.test = 'test'
                def func(self, foo):
                    if foo == 'foo' and self.test == 'test':
                        raise OkException

            self.assertRaises(OkException, apply, C().func, {'foo': 'foo'})


        def test_bound_method_new_style(self):
            class C(object):
                def __init__(self):
                    self.test = 'test'
                def func(self, foo):
                    if foo == 'foo' and self.test == 'test':
                        raise OkException

            self.assertRaises(OkException, apply, C().func, {'foo': 'foo'})


        def test_unbound_method(self):
            class C:
                def __init__(self):
                    self.test = 'test'
                def func(self, foo):
                    if foo == 'foo' and self.test == 'test':
                        raise OkException

            o = C()
            self.assertRaises(OkException, apply, C.func, {'self': o, 'foo': 'foo'})


        def test_callable_instance(self):
            class C:
                def __init__(self):
                    self.test = 'test'
                def __call__(self, foo):
                    if foo == 'foo' and self.test == 'test':
                        raise OkException

            o = C()
            self.assertRaises(OkException, apply, o, {'foo': 'foo'})


        def test_uncallable_instance(self):
            class C:
                def __init__(self):
                    self.test = 'test'

            o = C()
            self.assertRaises(AttributeError, apply, o, {})


        def test_staticmethod(self):
            class C:
                @staticmethod
                def foo(a, b=3):
                    if b == 3 and a == 10:
                        raise OkException

            self.assertRaises(OkException, apply, C().foo, {'a': 10})
            self.assertRaises(OkException, apply, C.foo, {'a': 10})


        def test_classmethod(self):
            class C:
                @classmethod
                def foo(cls, a, b=3):
                    if cls is not C:
                        raise ValueError('unknown class %r' % C)
                    if b == 3 and a == 10:
                        raise OkException

            self.assertRaises(OkException, apply, C().foo, {'a': 10})
            self.assertRaises(OkException, apply, C.foo, {'a': 10})


        def test_len(self):
            # can't call non-Python functions
            self.assertRaises(TypeError, apply, len, {})


        def test_class(self):
            class C:
                def __init__(self, foo):
                    if foo == 'foo':
                        raise OkException

            self.assertRaises(OkException, apply, C, {'foo': 'foo'})

        def test_new_style_class(self):
            class C(object):
                def __init__(self, foo):
                    if foo == 'foo':
                        raise OkException

            self.assertRaises(OkException, apply, C, {'foo': 'foo'})

        def test_no_init(self):
            # test old style
            class C():
                pass
            o = apply(C, {})
            self.assertTrue(isinstance(o, C))

        def test_no_init_new_style(self):
            # and new style
            class C(object):
                pass
            o = apply(C, {})
            self.assertTrue(isinstance(o, C))

        def test_derived(self):
            # ensure that base class __init__ functions are
            #  called
            class Base:
                def __init__(self, x):
                    self.x = x

            class Derived(Base):
                pass

            # or that derived class __init__ functions are
            #  called
            class Derived1(Base):
                def __init__(self, x):
                    self.x = x+1

            o = apply(Derived, {'x': 42})
            self.assertTrue(isinstance(o, Derived))
            self.assertEqual(o.x, 42)

            o = apply(Derived1, {'x': 41})
            self.assertTrue(isinstance(o, Derived1))
            self.assertEqual(o.x, 42)


        def test_derived_new_style(self):
            # ensure that base class __init__ functions are
            #  called
            class Base(object):
                def __init__(self, x):
                    self.x = x

            class Derived(Base):
                pass

            # or that derived class __init__ functions are
            #  called
            class Derived1(Base):
                def __init__(self, x):
                    self.x = x+1

            o = apply(Derived, {'x': 42})
            self.assertTrue(isinstance(o, Derived))
            self.assertEqual(o.x, 42)

            o = apply(Derived1, {'x': 41})
            self.assertTrue(isinstance(o, Derived1))
            self.assertEqual(o.x, 42)


    unittest.main()
