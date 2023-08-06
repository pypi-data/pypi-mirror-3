``withref`` makes Python's ``with`` statement able to simplify
complex dereferences.  This is what I initially, naively thought
the statement was for, similar to the ``with statement of half-remembered
Pascal. 

The typical Python use is a more complex guard over the entry and exit points
for using an object. See e.g. http://effbot.org/zone/python-with-statement.htm
But `withref` makes this simpler "just give me the dereferenced object, please"
use case work as well.

Usage
=====

::
  
    from withref import ref
    from easydict import EasyDict
    
    # EasyDict used for demonstration purposes only. Convenient way to
    # make dict entries accessible as dot-deferenceable properties.

    a = EasyDict({ 'b': { 'c': { 'c1': 1 }, 'd': 44.1 } })
    
    with ref(a.b.c) as c:
        c.c1 = 99

    print a
    a_ideal = EasyDict({'b': {'c': {'c1': 99}, 'd': 44.1}})
    assert a == a_ideal
    
It works with array-style references too, of course:
    
    with ref(a['b']['c']) as cc:
        c['c1'] = 99
        
    assert a == a_ideal
    
But beware OVER-dereferencing! While this works correctly:

    with ref(a.b.c.c1) as c1:
        print c1
        assert c1 == 99

This does NOT:

    with ref(a.b.c.c1) as c1:
        c1 = 12345
        assert c1 == 12345 
        
    assert a.b.c.c1 == 99   # with heavy heart

Unlike Pascal, ref is not built into the language proper. And unlike Perl,
Python is less eager to provide lvalues for every mention of a variable or
value. As a result, ``ref`` can provide the *value* of the full-deferenced
``c1``, but not the assignable *lvalue*.

Like Pascal's ``with``, ``ref`` removes N-1 layers of the enclosing structure
for values, but only N-2 for assignment. Still, in complex multi-layer
structures, this can be a nice simplification:

    with ref(app.config.server.wsgi) as wsgi:
        wsgi.logger = some_logger
        wsgi.debug_level = 4
        wsgi.port = 8080
        
arguably beats:

    app.config.server.wsgi.logger = some_logger
    app.config.server.wsgi.debug_level = 4
    app.config.server.wsgi.port = 8080

for simplicity and clarity.

I see a lot of configuration code that constantly repeats the same long
multi-level dereferences. That style is repetitive (anti-DRY) and tends to
left-align code blocks, both of which impede program comprehension. Using the
``with`` statement is a neat way to simplify and at the same time add a little extra
visual structure.

And while assignment ("lvalue production") isn't always possible, there still are
some interesting tricks possible with simple value production:

    with ref("this is a string"[0:4]) as t:
        print t

Alternative
===========

While ``yadda.yadda.yadda`` referencing is all too common, one can also
use a more proximate variable assignment:
    
    wsgi = app.config.server.wsgi
    wsgi.logger = some_logger
    wsgi.debug_level = 4
    wsgi.port = 8080
    
This lacks the more indented structure of the ``withref`` approach, but
is still much preferable to what you often find in the field.

See Also
========

The ``withhacks`` module <http://pypi.python.org/pypi/withhacks>, which includes
many other fun hacks (multi-line lambdas, new looping structures, etc.)--but
also requires the byteplay module <http://pypi.python.org/pypi/byteplay> which
actively introspects & munges Python bytecode ("Danger, Will Robinson!
Danger!"), and has not been updated to work beyond Python 2.6.

Possible Future Extension
=========================

As ``withhacks`` shows, using introspection we could determine the lvalue of the
calling object even in the edge-case where it is a leaf-node of its enclosing
structure. This would not require any bytecode changes, and should be compatible
with modern versions of Python (e.g. 2.7.x and 3.x).

Whether that trick can be done simply, portably, rock-solid reliably, and
transparently enough to satisfy those who code the modules that tend to most need
this kind of dereferencing simplification--i.e. complex modules often used in
production settings, into which they are understandably loathe to introduce any
possible sources of error or any performance impedance--that is the key open question.

Installation
============

::

    pip install withref
    
To use the test and demonstration code as shown here, also:

    pip install easydict
    
(You may need to prefix these with "sudo " to authorize installation.)
