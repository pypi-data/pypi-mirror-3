'''A module to access variables defined in calling frames.

Copyright 2012 by Kay-Uwe (Kiwi) Lorenz

Published under `New BSD License`_, see :file:`LICENSE.txt` for details.

Inspired by Perl6's ``$*foo`` variables, which are "dynamically overridable
global variables" (`Synopsis 2 on Twigils`_), I have created this module.

.. _Synopsis 2 on Twigils: http://perlcabal.org/syn/S02.html#Twigils

Basically this enables you to access local variables from calling frames::

    >>> def a(): x = 1 ; return b()
    >>> def b(): return ctx('x')
    >>> a()
    1

If you request to get a variable from calling contexts, there will be
searched locals of each calling frame until requested variable is found,
or there will be raised a *NameError* exception.

If you rely on this feature and you set a variable *x*, which should be 
accessed in a called function, you quickly hit the problem, that your *x*
might be used in another called function locally and you do not get the 
expected value in your called function, but the one of the other *x*::

    >>> def a(): x = 1 ; return b()
    >>> def b(): x = 2 ; return c()
    >>> def c(): # expects x from a 
    ...     return ctx('x')
    >>> a()
    2

So it is good to brand context variables with some characters, which cannot
be used in usual python syntax for variables::

    >>> def a(): ctx('*x', 1) ; return b()
    >>> def b(): x = 2 ; return c()
    >>> def c(): # expects *x from a
    ...    return ctx('*x')
    >>> a()
    1

If you try to access a variable, which cannot be found, there will be raised
a NameError::

    >>> ctx('***does not exist***')
    Traceback (most recent call last):
    ...
    NameError: name '***does not exist***' not defined in calling frames

You can use :func:`ctxget` for specifying a default in such a case:

    >>> ctxget('***does not exist***', 'default')
    'default'

There are two convenience functions for normal import::

    >>> import ctxvar
    >>> ctxvar.set('*foo', 'bar')
    >>> ctxvar.get('*foo', 'default')
    'bar'

If you access a context var more than once within a function, it may be 
helpful to copy it to local frame, while getting the value::

    >>> def a(): ctx('*x', 1) ; return b()
    >>> def b(): x = 2 ; return c()
    >>> def c(): # expects *x from a
    ...    first = ctx('*x', Here)
    ...    return ctx('*x') # this will access the local copy
    >>> a()
    1

    >>> def a(): FOO = "Hello" ; return b()
    >>> def b(): BAR = "World" ; return c()
    >>> def c(): return ctxstr("${FOO} ${BAR}")
    >>> a()
    'Hello World'

This will go back the frames only once.

'''
__all__        = [ 'ctx', 'ctxget', 'ctxstr', 'Here' ]
__copyright__  = "Copyright 2012, Kay-Uwe (Kiwi) Lorenz"
__author__     = "Kay-Uwe (Kiwi) Lorenz"
__email__      = "kiwi@franka.dyndns.org"
__license__    = "BSD-3"
__status__     = "Production"
__version__    = '1.0.3'
__docformat__ = 'restructuredtext'

import sys

if hasattr(sys, '_getframe'):
    getframe = sys._getframe
else:
    def _getframe():
        try:
            raise Exception
        except:
            return sys.exc_info()[2].tb_frame.f_back
    getframe = _getframe

class MyMetaClass(type):
    def __repr__(cls): return cls.__name__

class Undef:
    '''A Symbolic class different from `None` for use as default value in 
    a function, if `None` could be passed as value. See :func:`ctx`.
    '''
    __metaclass__ = MyMetaClass

class Here:
    '''A Symbolic class for indicating, that you want to copy a context
    variable into local scope. See :func:`ctx`.
    '''
    __metaclass__ = MyMetaClass

def find_ctx_var(name, count=1, frame=Undef, caching=None):
    """Return value of variable named *name* in calling frames.

    Parameters:
        `name`
            name of the variable to be found

        `count`
            return value of *count*th found variable, default 1

        `frame`
            frame_ where to start searching for the variable, 
            default is Undef, which means it will be automatically 
            determined.

        `caching`
            flag if the variable should be cached in each frame on 
            the way to the variable.

    Returns:
        value of variable

    Raises:
        `NameError` - if top level frame is reached and variable could not be
        found.

    .. _frame: http://docs.python.org/reference/datamodel.html#frame-objects

    """
    if frame is Undef:
        frame = getframe().f_back

    if frame is None:
        raise NameError("name '%s' not defined in calling frames" % name)

    f_back = frame.f_back

    if isinstance(name, (tuple, list)):
        return [ find_ctx_var(n, count, f_back, caching) for n in name ]

    try:
        result = frame.f_locals[name]

        if count <= 1: return result

        return find_ctx_var(name, count-1, f_back, caching)

    except KeyError:
        r = find_ctx_var(name, count, f_back, caching)

        if caching:
            # do this for caching. Maybe this is semantically incorrect 
            frame.f_locals[name] = r
        return r

def ctx(name, value=Undef, caching=None, back=1):
    '''Set or get a context variable.

    Parameters:
        `name`
            name of variable

        `value`
            Any value the variable shall be set to. Default is Undef, 
            a local class, which indicates that rather a value shall be 
            retrieved than stored.

            You may also set the value to Here, this will still retrieve 
            the value but will create a copy of the variable in current 
            frame.

        `caching`
            Set caching on, if there shall be created a copy in each 
            frame between current one and the one holding the variable. 
            Similar to *value* = *Here*.

        `back`
            Number of frames initially go back. This usually needs not 
            to be set and is rather for internal calls, see :func:`set`

    Returns:
        value of variable

    Raises:
        `NameError` - if top level frame is reached and variable could not be
        found.
    '''

    if caching is None:
        caching = ctx.CACHING

    frame = getframe()
    while back > 0:
        frame = frame.f_back
        back -= 1

    if value is Undef:
        return find_ctx_var(name, frame = frame, caching = caching)

    if value is Here:
        if isinstance(name, (tuple, list)):
            r = []
            for n in name:
                x = find_ctx_var(n, frame = frame, caching = caching)
                frame.f_locals[n] = x
                    
                r.append(x)
        else:
            r = find_ctx_var(name, frame = frame, caching = caching)
            frame.f_locals[name] = r
        return r
    else:
        frame.f_locals[name] = value

ctx.CACHING = None

def ctxget(name, default=None):
    '''get a context variable. If not exists return default value'''
    try:
        return ctx(name)
    except NameError:
        return default

get = ctxget

def set(name, value):
    '''set context variable name = value'''
    return ctx(name, value, back=2)

def _test(m=None, verbose=False):
    import doctest
    return doctest.testmod(m=m, verbose=verbose)

def ctxstr(s, default=""):
    '''expand each ${...} s to its ctxvar. if default is None, replace by match'''
    import re
    return re.sub(r"\$\{([^\}\s]+)\}", 
              lambda m: ctxget(m.group(1), default is None and m.group(0) or default), s)

if __name__ == "__main__":
    _test()
