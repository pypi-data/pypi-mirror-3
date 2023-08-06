
"""
constrict
=========
Constrict is a framework for adding type checking and constraints to functions.
Constraints are declared as function annotations (following the `typespec` 
format) and type checking is added using function decorators.

Constrict also provides a set of assertions for ad hoc type checking an a mix
in TestCase class for extending your unit tests.

Constrict depends on the ``typespec`` <https://github.com/galini/typespec> 
module and you should see the documentation of that module for details of how 
to format function arguments.

The Decorators
--------------

Import the decorators like so::

    >>> from constrict import checkargs, checkreturn, checkyield, check

Adding type checking for function arguments::

    >>> @checkargs
    ... def my_func_of_int(i : int) -> int:
    ...     return i + 1
    >>> my_func_of_int("hello")
    Traceback (most recent call last):
        ...
    constrict.ArgumentAssertionError: Invalid value 'hello' for argument i - i must be int.
    >>> my_func_of_int(1)
    2

Adding type checking for function return values::

    >>> @checkreturn
    ... def my_func_of_int(i : int) -> int:
    ...     return str(i+1)
    >>> my_func_of_int("hello")
    Traceback (most recent call last):
        ...
    TypeError: Can't convert 'int' object to str implicitly
    >>> my_func_of_int(1)
    Traceback (most recent call last):
        ...
    constrict.ReturnAssertionError: Invalid return value '2' - value must be int.

Adding type checking for yielded values::

    >>> @checkyield
    ... def my_generator() -> int:
    ...     for val in (1, 2, 3, "4", 5, 6):
    ...         yield val
    >>> for val in my_generator():
    ...     pass
    Traceback (most recent call last):
        ...
    constrict.YieldAssertionError: Invalid yielded value '4' - value must be int.

The ``check`` decorator is the same as using both ``checkargs`` and 
``checkreturn`` for a function or ``checkargs`` and ``checkyield`` for a 
generator.

The Assertions
--------------

Importing all assertions::

    >>> from constrict import (assert_isa, assert_valid, assert_valid_args,
    ...     assert_valid_return, assert_valid_yield, assert_call_ok, 
    ...     assert_iter_ok)

The assertions are functions that work like the ``assert`` statement. They do 
dynamic type checking and raise errors for invalid types. See the documentation
of each function for further details.

Using With unittest
-------------------

You can write test cases that check argument, return and yielded values.
Simply mix in the constrict.TestCase class into your test cases::

    import unittest
    import constrict
    
    class MyTestCase(unittest.TestCase, constrict.TestCase):
        def testSomething(self):
            ...

    if __name__ == '__main__':
        unittest.main()

This makes available extra test assertions that you can use.
See the documentation of the ``constrict.TestCase`` class for more details.

"""

__version__ = '1.0.0'

try:
    from typespec import isa, TypeSpec
except ImportError as e:
    if 'IGNORE_NO_TYPESPEC' in globals():
        def isa():
           pass
        class TypeSpec(object):
           pass
    else:
        raise e
import inspect

#Errors

class ConstrictTypeError(TypeError):
    def __init__(self,
        message : str,
        value : (object, "Invalid value."),
        expected : TypeSpec
    ):
        self.value = value
        self.expected = expected
        allowed = [t.__name__ for t in expected]
        super(ConstrictTypeError, self).__init__(
            message.replace('VAL', repr(value)).replace(
                'TYPE', ' or '.join(allowed))
        )

class ArgumentTypeError(ConstrictTypeError):
    message = 'Invalid value VAL for argument NAME - NAME must be TYPE.'
    def __init__(self, 
        name : (str, "Name of argument."),
        value : (object, "Invalid value."),
        expected : TypeSpec
    ):
        super(ArgumentTypeError, self).__init__(
            self.__class__.message.replace('NAME', name),
            value,
            expected
        )

class ReturnTypeError(ConstrictTypeError):
    message = 'Invalid return value VAL - value must be TYPE.'
    def __init__(self,
        value : (object, "Invalid value."),
        expected : TypeSpec
    ):
        super(ReturnTypeError, self).__init__(
            self.__class__.message,
            value,
            expected
        )

class YieldTypeError(ConstrictTypeError):
    message = 'Invalid yielded value VAL - value must be TYPE.'
    def __init__(self,
        value : (object, "Invalid value."),
        expected : TypeSpec
    ):
        super(YieldTypeError, self).__init__(
            self.__class__.message,
            value,
            expected
        )

class IsaAssertionError(ConstrictTypeError):
    message = 'VAL is not TYPE'
    def __init__(self, value, typ):
        super(IsaAssertionError, self).__init__(
            self.__class__.message, value, TypeSpec(typ))

class TypeSpecAssertionError(ConstrictTypeError):
    message = 'VAL is invalid - it should be TYPE'
    def __init__(self, value, expected):
        super(IsaAssertionError, self).__init__(
            self.__class__.message, value, expected)

class ArgumentAssertionError(ArgumentTypeError):
    pass

class ReturnAssertionError(ReturnTypeError):
    pass

class YieldAssertionError(YieldTypeError):
    pass


#Assertions

def assert_isa(val, typ : type):
    """
    Assert that ``val`` is a ``typ``.
    This uses the ``typespec.isa`` function so supports validation classes.
    """
    try:
        assert isa(val, typ)
    except AssertionError:
        raise IsaAssertionError(val, typ)

def assert_valid(val, ts : TypeSpec):
    """
    Assert that ``val`` successfully validates against the TypeSpec ``ts``.
    """
    try:
        assert val in ts
    except AssertionError:
        raise TypeSpecAssertionError(val, typ)

def assert_valid_return(
    fn : "The function that the return value must be valid for.",
    val : "The return value"):
    """
    Assert that ``val`` is a valid return value for the function ``fn``.
    """
    try:
        assert inspect.isfunction(fn)
    except AssertionError:
        raise TypeError("``fn`` is not a function.")
    if 'return' in fn.__annotations__:
        ts = TypeSpec(fn.__annotations__['return'])
        try:
            assert val in ts
        except AssertionError:
            raise ReturnAssertionError(val, ts)

def assert_valid_yield(
    fn : "The function that the yielded value must be valid for.",
    val : "The yielded value"):
    """
    Assert that ``val`` is a valid yielded value for the generator function 
    ``fn``.
    """
    try:
        assert inspect.isgeneratorfunction(fn)
    except AssertionError:
        raise TypeError("``fn`` is not a generator function.")
    if 'return' in fn.__annotations__:
        ts = TypeSpec(fn.__annotations__['return'])
        try:
            assert val in ts
        except AssertionError:
            raise YieldAssertionError(val, ts)

def assert_valid_args(fn, *args, **kwargs):
    """
    Assert that the arguments given are valid for the function ``fn``.
    """
    try:
        assert inspect.isfunction(fn)
    except AssertionError:
        raise TypeError("``fn`` is not a function.")
    argspec = inspect.getfullargspec(fn)
    i = 0
    for arg in argspec.args:
        if arg in argspec.annotations:
            ts = TypeSpec(argspec.annotations[arg])
            if i >= len(args):
                raise AssertionError('Wrong number of arguments.')
            if not args[i] in ts:
                raise ArgumentAssertionError(arg, args[i], ts)
        i += 1
    for arg in argspec.kwonlyargs:
        try:
            assert arg in argspec.kwonlydefaults or arg in kwargs
        except AssertionError:
            raise AssertionError(
                "Required keyword only argument %s is not present." % arg
            )
        if arg in argspec.annotations and arg in kwargs:
            ts = TypeSpec(argspec.annotations[arg])
            if not kwargs[arg] in ts:
                raise ArgumentAssertionError(arg, args[i], ts)

def assert_call_ok(fn, *args, **kwargs):
    """
    Assert that the arguments given are valid for the function ``fn`` then
    call the function and assert that the return value is valid.
    """
    assert_valid_args(fn, *args, **kwargs)
    assert_valid_return(fn, fn(*args, **kwargs))

def assert_iter_ok(fn, *args, **kwargs):
    """
    Assert that the arguments given are valid for the generator function ``fn``
    then iterate over yielded values and assert that they are valid.
    """
    assert_valid_args(fn, *args, **kwargs)
    for val in fn(*args, **kwargs):
        assert_valid_yield(fn, val)


#Decorators

def checkargs(fn):
    """
    Decorator: check that the args are valid before calling the function.
    """
    def wrapper(*args, **kwargs):
        assert_valid_args(fn, *args, **kwargs)
        return fn(*args, **kwargs)
    return wrapper

def checkreturn(fn):
    """
    Decorator: check that the return value of the function is valid.
    """
    def wrapper(*args, **kwargs):
        r = fn(*args, **kwargs)
        assert_valid_return(fn, r)
        return r
    return wrapper

def checkyield(fn):
    """
    Decorator: check that the return value of the function is valid.
    """
    def wrapper(*args, **kwargs):
        for y in fn(*args, **kwargs):
            assert_valid_yield(fn, y)
            yield y
    return wrapper

def check(fn):
    """
    Decorator: check that the arguments of the function and its return value or
    yielded values are valid.
    """
    if inspect.isgeneratorfunction(fn):
        return checkyield(checkargs(fn))
    else:
        return checkreturn(checkargs(fn))

#Unit Testing


def _assertion(assertion_fn):
    def dec(fn):
        def wrapper(self, *args, **kwargs):
            try:
                assertion_fn(*args, **kwargs)
            except AssertionError as e:
                self.fail(e.args[0])
        wrapper.__doc__ = ''.join(('self.',
            fn.__name__,
            inspect.formatargspec(*inspect.getfullargspec(assertion_fn)),
            "\n", assertion_fn.__doc__))
        return wrapper
    return dec


class TestCase(object):
    @_assertion(assert_isa)
    def assertIsa(self):
        pass

    @_assertion(assert_valid)
    def assertValid(self):
        pass

    @_assertion(assert_valid_args)
    def assertValidArgs(self):
        pass

    @_assertion(assert_valid_return)
    def assertValidReturn(self):
        pass

    @_assertion(assert_valid_yield)
    def assertValidYield(self):
        pass

    @_assertion(assert_call_ok)
    def assertCallOk(self):
        pass

    @_assertion(assert_iter_ok)
    def assertIterOk(self):
        pass

