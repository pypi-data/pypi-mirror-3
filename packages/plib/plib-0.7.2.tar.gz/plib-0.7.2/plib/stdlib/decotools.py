#!/usr/bin/env python
"""
Module DECOTOOLS -- Decorator Functions and Factories
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.stdlib.func import partial, wraps


def cached_property(func):
    """Decorator for cached property.
    
    This decorator works the same as the built-in ``property``
    decorator, but caches the property value in the instance
    dictionary so that the underlying function is only called
    once. The property is read-only.
    """
    
    from plib.stdlib import CachedProperty
    return CachedProperty(func)


def cached_function(func):
    """Decorator to cache function results by arguments.
    
    We "tuple-ize" the keyword arguments dictionary since
    dicts are mutable; keywords themselves are strings and
    so are always hashable, but if any arguments (keyword
    or positional) are non-hashable, that set of arguments
    is not cached.
    """
    
    cache = {}
    
    @wraps(func)
    def _decorated(*args, **kwds):
        key = args + tuple(kwds.iteritems())
        try:
            result = cache.get(key, None)
        except TypeError:
            # Can't cache this set of arguments
            result = key = None
        if result is None:
            result = func(*args, **kwds)
            if key is not None:
                cache[key] = result
        return result
    
    return _decorated


def cached_class(klass):
    """Decorator to cache class instances by constructor arguments.
    
    This is basically the cached_function decorator applied to
    the __new__ method, with a couple of extra features to make
    it work properly with classes.
    
    Typical usage:
        
        >>> @cached_class
        ... class Test(object):
        ...     def __init__(self, *args, **kwds):
        ...         self.args = args
        ...         self.kwds = kwds
        ...
        >>> t1 = Test(0, a=1)
        >>> t1.args
        (0,)
        >>> t1.kwds
        {'a': 1}
    
    A second call to the class with the same arguments will
    return the same instance:
    
        >>> t1a = Test(0, a=1)
        >>> t1a.args
        (0,)
        >>> t1a.kwds
        {'a': 1}
        >>> t1a is t1
        True
    
    Each new set of arguments creates a new instance; partial
    matches are still new sets of arguments:
    
        >>> t2 = Test(1, b=2)
        >>> t2.args
        (1,)
        >>> t2.kwds
        {'b': 2}
        >>> t2 is t1
        False
        >>> t3 = Test(0, b=2)
        >>> t3.args
        (0,)
        >>> t3.kwds
        {'b': 2}
        >>> any(t3 is t for t in (t1, t2))
        False
        >>> t4 = Test(1, a=1)
        >>> t4.args
        (1,)
        >>> t4.kwds
        {'a': 1}
        >>> any(t4 is t for t in (t1, t2, t3))
        False
    
    An empty set of arguments is also treated as a distinct
    set of arguments and is cached like any other:
    
        >>> t5 = Test()
        >>> t5.args
        ()
        >>> t5.kwds
        {}
        >>> any(t5 is t for t in (t1, t2, t3, t4))
        False
        >>> t5a = Test()
        >>> t5a is t5
        True
    
    The same goes for positional-only or keyword-only sets
    of arguments:
    
        >>> t6 = Test(0)
        >>> t6.args
        (0,)
        >>> t6.kwds
        {}
        >>> any(t6 is t for t in (t1, t2, t3, t4, t5))
        False
        >>> t6a = Test(0)
        >>> t6a is t6
        True
        >>> t7 = Test(a=1)
        >>> t7.args
        ()
        >>> t7.kwds
        {'a': 1}
        >>> any(t7 is t for t in (t1, t2, t3, t4, t5, t6))
        False
        >>> t7a = Test(a=1)
        >>> t7a is t7
        True
    
    There is also no possibility of "overlap" between
    positional and keyword arguments, even if they have
    the same values:
    
        >>> t8 = Test('a', 'a')
        >>> t8.args
        ('a', 'a')
        >>> t8.kwds
        {}
        >>> t9 = Test(a='a')
        >>> t9.args
        ()
        >>> t9.kwds
        {'a': 'a'}
        >>> t9 is t8
        False
        >>> t10 = Test('a', a='a')
        >>> t10.args
        ('a',)
        >>> t10.kwds
        {'a': 'a'}
        >>> t10 is t8
        False
        >>> t10 is t9
        False
    
    Finally, unhashable arguments return a new instance
    each time, even for values that compare equal:
    
        >>> t11 = Test([])
        >>> t12 = Test([])
        >>> t11 is t12
        False
        >>> (t11.args == t12.args) and (t11.kwds == t12.kwds)
        True
        >>> t13 = Test(a=[])
        >>> t14 = Test(a=[])
        >>> t13 is t14
        False
        >>> (t13.args == t14.args) and (t13.kwds == t14.kwds)
        True
        >>> t15 = Test([], a=[])
        >>> t16 = Test([], a=[])
        >>> t15 is t16
        False
        >>> (t15.args == t16.args) and (t15.kwds == t16.kwds)
        True
    """
    
    @wraps(klass, assigned=('__name__', '__module__'), updated=())
    class _decorated(klass):
        # The wraps decorator can't do this because __doc__
        # isn't writable once the class is created
        __doc__ = klass.__doc__
        
        @cached_function
        def __new__(cls, *args, **kwds):
            # Technically this is cheating, but it works,
            # and takes care of initializing the instance
            # (so we can override __init__ below safely);
            # calling up to klass.__new__ would be the
            # "official" way to create the instance, but
            # that raises DeprecationWarning if there are
            # args or kwds and klass does not override
            # __new__ (which most classes don't), because
            # object.__new__ takes no parameters (and in
            # Python 3 the warning will become an error)
            inst = klass(*args, **kwds)
            # This makes isinstance and issubclass work
            # properly
            inst.__class__ = _decorated
            return inst
        
        def __init__(self, *args, **kwds):
            # This will be called every time __new__ is
            # called, so we skip initializing here and do
            # it only when the instance is created above
            pass
    
    return _decorated


def test_required(test_func, fail_func):
    """General pattern for decorators with pretest and failure functions.
    
    Parameters:
    
        ``test_func`` is called with the same arguments as the decorated
            function; it must return a true value for the decorated function
            to be called.
        
        ``fail_func`` is called with the same arguments as the decorated
            function if ``test_func`` returns a false value.
    
    Example, similar to a simple web app user login use case::
    
        >>> users = ['alice', 'bob']
        >>> def test_user(username):
        ...     return username in users
        ... 
        >>> def failed_user(username):
        ...     return username + " is not a known user."
        ... 
        >>> login_required = test_required(test_user, failed_user)
        >>> @login_required
        ... def user_login(username):
        ...     return username + " is logged in."
        ... 
        >>> user_login('alice')
        'alice is logged in.'
        >>> user_login('bob')
        'bob is logged in.'
        >>> user_login('charlie')
        'charlie is not a known user.'
        >>> 
    """
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwds):
            if test_func(*args, **kwds):
                return f(*args, **kwds)
            return fail_func(*args, **kwds)
        return decorated_function
    return decorator


def merge_dict(target, source):
    """Merges source into target."""
    merges = dict((key, value) for key, value in source.iteritems()
        if key not in target)
    target.update(merges)


def decorator_prep_result(prep_func=None, result_func=None,
        *d_args, **d_kwds):
    """General pattern for decorators with preparation and result functions.
    
    Parameters:
    
    - ``prep_func`` will be passed the ``d_args`` and ``d_kwds`` passed to
      the decorator, and should return a tuple ``(args, kwds)``, where
      ``args`` and ``kwds`` are positional and keyword arguments to be
      passed to the result function; or, it can return ``None`` (the default
      if it is a procedure and doesn't explicitly return a value), in which
      case the ``d_args`` and ``d_kwds`` will be passed on unchanged to
      the result function (this is expected to be the common case).
      
    - ``result_func`` will be passed the positional and keyword arguments that
      result from processing by ``prep_func`` above, and by the decorated
      function itself, which can return a ``dict`` of keyword arguments that
      will be used to update those coming from ``prep_func``.
    
    Examples, similar to a simple web app templating use case:
    
    - The simplest usage is a decorated function that does nothing, all of
      the work is in the decorator itself; this usage is for arguments that
      are known at import time::
    
        >>> def render_template(filename):
        ...     return "Template rendered: " + filename
        ... 
        >>> def templated(filename):
        ...     return decorator_prep_result(None, render_template, filename)
        ... 
        >>> @templated("test.html")
        ... def test():
        ...     pass
        ... 
        >>> test()
        'Template rendered: test.html'
    
    - Alternatively, we can pass arguments by having the decorated function
      return a dict, if the arguments are only known at run time::
    
        >>> def templated_alt():
        ...     return decorator_prep_result(None, render_template)
        ... 
        >>> @templated_alt()
        ... def test_alt(filename):
        ...     return dict(filename=filename)
        ... 
        >>> test_alt("test.html")
        'Template rendered: test.html'
    
    - Be careful not to pass the same argument both ways, however::
    
        >>> @templated("test1.html")
        ... def test_bad(filename):
        ...     return dict(filename=filename)
        ...
        >>> test_bad("test2.html")
        Traceback (most recent call last):
         ...
        TypeError: render_template() got multiple values for keyword argument 'filename'
    
    - We can also pass keyword arguments via the decorator at import time::
    
        >>> def templated_kwd(filename):
        ...     return decorator_prep_result(None, render_template, filename=filename)
        ... 
        >>> @templated_kwd(filename="test.html")
        ... def test_kwd():
        ...     pass
        ... 
        >>> test_kwd()
        'Template rendered: test.html'
    
    - But remember that keyword arguments passed via the decorator will be
      overridden by keyword arguments passed at runtime via the decorated
      function (note the difference from the case above where we passed the
      argument positionally in the decorator)::
    
        >>> @templated_kwd(filename="notseen.html")
        ... def test_kwd_update(filename):
        ...     return dict(filename=filename)
        ... 
        >>> test_kwd_update("test.html")
        'Template rendered: test.html'
    
    - Also, we can add a preparation function to massage arguments passed to
      the decorator; but note that this is less convenient because we have to
      return a tuple ``(args, kwds)``::
    
        >>> import os
        >>> def massage_path(basename):
        ...     return (basename.replace("test", "massaged"),), {}
        ... 
        >>> def templated_prep(basename):
        ...     return decorator_prep_result(massage_path, render_template, basename)
        ... 
        >>> @templated_prep("test.html")
        ... def test_prep():
        ...     pass
        ... 
        >>> test_prep()
        'Template rendered: massaged.html'
    
    - And, of course, we can combine all of the above (note that we pass all
      arguments as keyword arguments to ensure no collisions, since the
      ordering is reversed--the template argument comes after the decorated
      function argument in the result function's signature)::
    
        >>> def render_template_in_dir(dirname, basename):
        ...     return "Template rendered: " + basename + " in directory " + dirname
        ... 
        >>> def massage_basename(basename):
        ...     return (), {'basename': basename.replace("test", "massaged")}
        ... 
        >>> def templated_combined(basename):
        ...     return decorator_prep_result(massage_basename, render_template_in_dir, basename=basename)
        ... 
        >>> @templated_combined("test.html")
        ... def test_combined(dirname):
        ...     return dict(dirname=dirname)
        ... 
        >>> test_combined("testdir")
        'Template rendered: massaged.html in directory testdir'
    
    - Finally, note that, even though ``result_func`` is given a default
      argument in the function signature above, we can't omit it (we shouldn't
      want to anyway, since if we could it would just be a roundabout way of
      forming a closure)::
    
        >>> @decorator_prep_result()
        ... def test_no_result_func():
        ...     pass
        ... 
        >>> test_no_result_func()
        Traceback (most recent call last):
         ...
        TypeError: 'NoneType' object is not callable
        >>> 
    """
    
    def decorator(f):
        p = None
        if prep_func:
            p = prep_func(*d_args, **d_kwds)
            if p:
                r_args, f_kwds = p
        if not p:
            r_args, f_kwds = d_args, d_kwds.copy()
        @wraps(f)
        def decorated_function(*args, **kwds):
            r_kwds = (f(*args, **kwds) or {})
            merge_dict(r_kwds, f_kwds)
            return result_func(*r_args, **r_kwds)
        return decorated_function
    return decorator


def decorator_with_f(f, decorator):
    """Allows decorator to be used either with or without parameters.
    
    For example, let's modify the above web app login use case::
    
    - We set up a login_required decorator we can use with no arguments,
      as above (note that we have to give defaults for all arguments, and
      in particular the first argument ``f`` must default to ``None``)::
    
        >>> users = ['alice', 'bob']
        >>> def test_user(username):
        ...     return username in users
        ... 
        >>> def failed_user(username):
        ...     return username + " is not a known user."
        ... 
        >>> def login_required(f=None, test=test_user, failed=failed_user):
        ...     return decorator_with_f(f, test_required(test, failed))
        ... 
        >>> @login_required
        ... def user_login(username):
        ...     return username + " is logged in."
        ... 
        >>> user_login('alice')
        'alice is logged in.'
        >>> user_login('bob')
        'bob is logged in.'
        >>> user_login('charlie')
        'charlie is not a known user.'
    
    - But now we can use the same decorator with different functions, by
      passing them as arguments (note that they have to be keyword arguments
      so that the first, function argument will be ``None``, as needed)::
    
        >>> admins = ['alice']
        >>> def test_admin(username):
        ...     return username in admins
        ... 
        >>> def failed_admin(username):
        ...     if test_user(username):
        ...         return username + " is not an admin."
        ...     return failed_user(username)
        ... 
        >>> @login_required(test=test_admin, failed=failed_admin)
        ... def admin_login(username):
        ...     return username + " is logged in as an admin."
        ... 
        >>> admin_login('alice')
        'alice is logged in as an admin.'
        >>> admin_login('bob')
        'bob is not an admin.'
        >>> admin_login('charlie')
        'charlie is not a known user.'
        >>> 
    """
    
    if f is None:
        return decorator
    return decorator(f)


def delay(decorator):
    """Allows decorator to delay until its function is invoked.
    
    Typical usage and comparison with normal decorators:
    
        >>> def decorator(f):
        ...     print "Decorating", f.__name__
        ...     return f
        ...
        >>> @decorator
        ... def test1():
        ...     print "Tested!"
        ...
        Decorating test1
        >>> test1()
        Tested!
        >>> test1()
        Tested!
    
    Unlike the normal decorator, the delayed decorator gets applied
    at function invocation, not function creation:
    
        >>> @delay
        ... def deco(f):
        ...    return decorator(f)
        ...
        >>> @deco
        ... def test2():
        ...     print "Tested again!"
        ...
        >>> test2()
        Decorating test2
        Tested again!
    
    But it still only gets applied once:
    
        >>> test2()
        Tested again!
    
    Now we test how things work when decorating a method:
    
        >>> class TestA(object):
        ...     @decorator
        ...     def test3(self):
        ...         print "Test from", self.__class__.__name__
        ...
        Decorating test3
        >>> a = TestA()
        >>> aa = TestA()
        >>> a.test3()
        Test from TestA
        >>> aa.test3()
        Test from TestA
        >>> aa.test3()
        Test from TestA
        >>> a.test3()
        Test from TestA
    
    Not only does the delayed decorator get applied at method
    invocation, not class creation, it gets applied separately
    for each instance:
    
        >>> class TestB(object):
        ...     @deco
        ...     def test4(self):
        ...         print "Test from", self.__class__.__name__
        ...
        >>> b = TestB()
        >>> bb = TestB()
        >>> b.test4()
        Decorating test4
        Test from TestB
        >>> bb.test4()
        Decorating test4
        Test from TestB
    
    But again, it still only gets applied once per instance:
    
        >>> bb.test4()
        Test from TestB
        >>> b.test4()
        Test from TestB
    
    See the ``DelayedDecorator`` module for more information.
    """
    
    from plib.stdlib import DelayedDecorator
    return partial(DelayedDecorator, decorator)


@delay
def memoize_generator(gen):
    """Memoizes a generator so each term is only computed once.
    
    Typical usage and comparison with non-memoized generators:
    
        >>> def gen():
        ...     for n in xrange(2):
        ...         print "Yielding", n
        ...         yield n
        ...     print "Stopping"
        ...
        >>> g1 = gen()
        >>> g2 = gen()
        >>> next(g1)
        Yielding 0
        0
        >>> next(g2)
        Yielding 0
        0
        >>> next(g2)
        Yielding 1
        1
        >>> next(g1)
        Yielding 1
        1
    
    Doctests don't like having exception output mixed in with
    ordinary output, so we trap the exception and use the
    normal output to detect generator exhaustion (we do this
    because we want to see the normal output, to tell whether
    the code after the last yield runs):
    
        >>> def tryit(g):
        ...     try:
        ...         next(g)
        ...     except StopIteration:
        ...         pass
        >>> tryit(g1)
        Stopping
        >>> tryit(g2)
        Stopping
    
    Now we try it with the generator memoized; we create two
    instances of it and see if they share the computation:
    
        >>> @memoize_generator
        ... def gen2():
        ...     return gen()
        >>> g3 = gen2()
        >>> g4 = gen2()
        >>> next(g3)
        Yielding 0
        0
        >>> next(g4)
        0
    
    The second generator didn't recompute term 0, it used the
    value that the first computed; now we'll let the second one
    go first for term 1:
    
        >>> next(g4)
        Yielding 1
        1
        >>> next(g3)
        1
    
    Even generator exhaustion only happens once; after that the
    other copies just end without rerunning the code after the
    last yield:
    
        >>> tryit(g3)
        Stopping
        >>> tryit(g4)
    
    A given generator is memoized separately for each different
    set of arguments:
    
        >>> @memoize_generator
        ... def gen(a, b=None):
        ...     print "Yielding", a
        ...     yield a
        ...     if b is not None:
        ...         print "Yielding", b
        ...         yield b
        ...
        >>> g1 = gen(0)
        >>> g2 = gen(0)
        >>> list(g1)
        Yielding 0
        [0]
        >>> list(g2)
        [0]
        >>> g3 = gen(1)
        >>> g4 = gen(1)
        >>> list(g3)
        Yielding 1
        [1]
        >>> list(g4)
        [1]
    
    Note that positional and keyword arguments are considered
    different, even if their values are the same:
    
        >>> g5 = gen(0, 1)
        >>> g6 = gen(0, 1)
        >>> list(g5)
        Yielding 0
        Yielding 1
        [0, 1]
        >>> list(g6)
        [0, 1]
        >>> g7 = gen(0, b=1)
        >>> list(g7)
        Yielding 0
        Yielding 1
        [0, 1]
        >>> g8 = gen(0, b=1)
        >>> list(g8)
        [0, 1]
    
    More illustrations of what are considered distinct sets of
    arguments:
    
        >>> g8 = gen(0, 2)
        >>> g9 = gen(0, b=2)
        >>> g10 = gen(a=0, b=2)
        >>> g11 = gen(1, 2)
        >>> g12 = gen(1, b=2)
        >>> g13 = gen(a=1, b=2)
        >>> g14 = gen(0, 3)
        >>> g15 = gen(0, b=3)
        >>> g16 = gen(a=0, b=3)
        >>> list(g8)
        Yielding 0
        Yielding 2
        [0, 2]
        >>> list(g9)
        Yielding 0
        Yielding 2
        [0, 2]
        >>> list(g10)
        Yielding 0
        Yielding 2
        [0, 2]
        >>> list(g11)
        Yielding 1
        Yielding 2
        [1, 2]
        >>> list(g12)
        Yielding 1
        Yielding 2
        [1, 2]
        >>> list(g13)
        Yielding 1
        Yielding 2
        [1, 2]
        >>> list(g14)
        Yielding 0
        Yielding 3
        [0, 3]
        >>> list(g15)
        Yielding 0
        Yielding 3
        [0, 3]
        >>> list(g16)
        Yielding 0
        Yielding 3
        [0, 3]
    
    See the ``MemoizedGenerator`` module for more information.
    """
    
    from plib.stdlib import MemoizedGenerator
    return MemoizedGenerator(gen)


@delay
def indexable_generator(gen):
    """Make a generator indexable like a sequence.
    
    Typical usage:
        
        >>> @indexable_generator
        ... def numgen():
        ...     for i in xrange(10):
        ...         print "Yielding", i
        ...         yield i
        ...
        >>> ng = numgen()
        >>> for n in ng:
        ...     print n
        ...
        Yielding 0
        0
        Yielding 1
        1
        Yielding 2
        2
        Yielding 3
        3
        Yielding 4
        4
        Yielding 5
        5
        Yielding 6
        6
        Yielding 7
        7
        Yielding 8
        8
        Yielding 9
        9
    
    Now that the generator is exhausted, further iteration
    won't yield any more items, and explicit calls to ``next``
    will raise ``StopIteration``:
    
        >>> for n in ng:
        ...     print n
        ...
        >>> next(ng)
        Traceback (most recent call last):
         ...
        StopIteration
    
    We can still continue to index into the generator like a
    sequence, even though it is exhausted:
    
        >>> for k in xrange(10):
        ...     print ng[k]
        ...
        0
        1
        2
        3
        4
        5
        6
        7
        8
        9
    
    If we realize the generator again, we can iterate through
    it again, but we won't actually advance the underlying
    generator any more; it is already exhausted and we are
    retrieving items from the cache:
    
        >>> for n in numgen():
        ...     print n
        ...
        0
        1
        2
        3
        4
        5
        6
        7
        8
        9
    
    The same goes for explicit calls to ``next``; we can
    start iteration over again but only from the cache:
    
        >>> next(numgen())
        0
        >>> next(numgen())
        0
    
    Indexing into the generator forces it to iterate to the
    requested index:
    
        >>> @indexable_generator
        ... def numgen1():
        ...     for i in xrange(10):
        ...         print "Yielding", i
        ...         yield i
        ...
        >>> ng1 = numgen1()
        >>> ng1[4]
        Yielding 0
        Yielding 1
        Yielding 2
        Yielding 3
        Yielding 4
        4
    
    Requesting an index that's already been iterated past in
    the underlying generator will, once again, retrieve from
    the cache:
    
        >>> ng1[2]
        2
    
    Note that indexing is separate from iteration, just as with
    a regular sequence; we can still iterate over all the items
    one time, even though we've indexed halfway in (so we only see
    the underlying generator yield for the last 5 items, the first
    5 come from the cache):
    
        >>> for n in ng1:
        ...     print n
        ...
        0
        1
        2
        3
        4
        Yielding 5
        5
        Yielding 6
        6
        Yielding 7
        7
        Yielding 8
        8
        Yielding 9
        9
    
    But again, we can only iterate once for a given realization
    of the generator:
    
        >>> for n in ng1:
        ...     print n
        ...
    
    Note that if the generator has not been exhausted, negative
    indexes don't work, because we don't have a sequence length
    to normalize them to:
    
        >>> @indexable_generator
        ... def numgen2():
        ...     for i in xrange(10):
        ...         print "Yielding", i
        ...         yield i
        ...
        >>> ng2 = numgen2()
        >>> ng2[0]
        Yielding 0
        0
        >>> ng2[-1]
        Traceback (most recent call last):
         ...
        IndexError: sequence index out of range
    
    However, once the generator is exhausted, it knows its
    length, and negative indexes will now work (note that
    asking for a high enough *positive* index has the effect
    of exhausting the generator, but it is not exhausted until
    we go beyond the last item, not just to it):
    
        >>> ng2[9]
        Yielding 1
        Yielding 2
        Yielding 3
        Yielding 4
        Yielding 5
        Yielding 6
        Yielding 7
        Yielding 8
        Yielding 9
        9
        >>> ng2[-1]
        Traceback (most recent call last):
         ...
        IndexError: sequence index out of range
        >>> ng2[10]
        Traceback (most recent call last):
         ...
        IndexError: sequence index out of range
        >>> ng2[-1]
        9
    
    Slicing behavior works similarly, except that a missing end index
    will raise ``IndexError`` just like a negative index, until the
    generator is exhausted:
    
        >>> @indexable_generator
        ... def numgen3():
        ...     for n in xrange(10):
        ...         print "Yielding", n
        ...         yield n
        ...
        >>> ng3 = numgen3()
        >>> ng3[0:5]
        Yielding 0
        Yielding 1
        Yielding 2
        Yielding 3
        Yielding 4
        (0, 1, 2, 3, 4)
        >>> ng3[0:5:2]
        (0, 2, 4)
        >>> ng3[:5:2]
        (0, 2, 4)
        >>> ng3[4::-2]
        (4, 2, 0)
        >>> ng3[0:]
        Traceback (most recent call last):
         ...
        IndexError: sequence index out of range
        >>> ng3[:-1]
        Traceback (most recent call last):
         ...
        IndexError: sequence index out of range
        >>> ng3[-1:]
        Traceback (most recent call last):
         ...
        IndexError: sequence index out of range
        >>> ng3[-1:5]
        Traceback (most recent call last):
         ...
        IndexError: sequence index out of range
    
    However, once the generator is exhausted, it behaves just
    like an ordinary sequence that knows its length (but note
    that, again, we actually have to exhaust it first, not
    just go to the last item but iterate beyond it):
    
        >>> ng3[5:10]
        Yielding 5
        Yielding 6
        Yielding 7
        Yielding 8
        Yielding 9
        (5, 6, 7, 8, 9)
        >>> ng3[0:10]
        (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        >>> ng3[:10]
        (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        >>> len(ng3)
        Traceback (most recent call last):
         ...
        TypeError: object of type indexediterator has no len()
        >>> ng3[:11]
        Traceback (most recent call last):
         ...
        IndexError: sequence index out of range
        >>> len(ng3)
        10
        >>> ng3[:]
        (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        >>> ng3[::]
        (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        >>> ng3[::-1]
        (9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
        >>> ng3[-1:]
        (9,)
        >>> ng3[:-1]
        (0, 1, 2, 3, 4, 5, 6, 7, 8)
    
    See the ``IndexedGenerator`` module for more information.
    """
    
    from plib.stdlib import IndexedGenerator
    return IndexedGenerator(gen)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
