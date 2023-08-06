"""Helper for the Python with statement. Helps developers more
neatly, simply, and cleanly access deeply-nested data structures."""

class ref(object):
    """Simple with statement guard objects."""
    
    def __init__(self, obj):
        """Mint one!"""
        self.obj = obj
        
    def __enter__(self):
        """Here we go!"""
        return self.obj
    
    def __exit__(self, _type, value, traceback):
        """Well, that was fun!"""
        if isinstance(value, Exception):
            raise value
        else:
            return True


if __name__ == '__main__':
    
    from easydict import EasyDict
    
    # EasyDict used for demonstration purposes only. Convenient way to
    # make dict entries accessible as dot-deferenceable properties.

    a = EasyDict({ 'b': { 'c': { 'c1': 1 }, 'd': 44.1 } })
    
    assert a.b.c.c1 == 1
    
    with ref(a.b.c) as c:
        c.c1 = 99
        assert c.c1 == 99
        assert a.b.c.c1 == 99

    print a
    a_ideal = EasyDict({'b': {'c': {'c1': 99}, 'd': 44.1}})
    assert a == a_ideal        

    # It works with array-style references too, of course:
    
    with ref(a['b']['c']) as cc:
        c['c1'] = 99
        
    assert a == a_ideal
    
    # But beware over-defreferencing. This works:
        
    with ref(a.b.c.c1) as c1:
        print c1
        assert c1 == 99     # so far, so good!
        c1 = 12345
        print c1
        assert c1 == 12345  # still good!
        
    # but c1 is just a local value there, and not the end value
    assert a.b.c.c1 == 99   # with heavy heart
    
    # Python produces values, not lvalues, so must retain one level of assignable
    # structure (e.g. dict, array, etc.)
    
    # But still might be useful for value production:

    with ref("this is a string"[0:4]) as t:
        print t
        assert t == "this"