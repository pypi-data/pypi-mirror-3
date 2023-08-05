"""Global substitution for Python unit tests

Provides substitution in all dictionaries throughout the interpreter,
this includes references held by objects and modules.  Restores those 
references which were replaced (only), i.e. you can re-use the objects
you used as substitutions after restoring.

Sample usage:

    >>> import globalsub
    >>> def x():
    ...     print 'x'
    ... 
    >>> def y():
    ...     print 'y'
    ... 
    >>> globalsub.subs( x, y )
    <function y at 0xb7470a04>
    >>> x()
    y
    >>> y()
    y
    >>> globalsub.restore( x )
    <function x at 0xb74709cc>
    >>> x()
    x
    >>> y()
    y

Sample usage for a test case:

    import globalsub as gs
    class Test(TestCase):
        def setUp( self ):
            gs.subs( somefunction, replacement )
        def tearDown( self ):
            gs.restore( somefunction )

Notes:

    * if you need to refer to the original function, store a
      reference in a list or tuple
    * corollary of that is that you likely do *not* want to store 
      function references in lists and iterate over them to substitute,
      if you do, you will need to capture the instances returned from 
      subs() and do a restore on them.
    * certain fixed-attribute values (SUBS_TYPES) will be replaced with 
      copies of the object which can receive arbitrary attributes.  
      List objects, however, cannot be so wrapped because they are mutable 
      and you may need their identities to remain the same.  You can 
      explicitly wrap them with globalsub.List( [] ) to make them 
      subs-compatible.

    * do *not* use the same object as the value-to-substitute for 
      more than one name/variable; only the *last* item will be 
      substituted; you will only be able to restore the last item 
      subs()'d.
"""
__version__ = '1.0.1'
import gc,logging 
log = logging.getLogger(__name__)

__all__ = ['subs','restore','List']

class List( list ):
    """Use to wrap your lists so that they can be subs'd"""

SUBS_TYPES = (str,unicode,int,long,float,tuple,complex,set,bool,)
def subsable( x ):
    """For builtin types that do not allow arbitrary attributes, subclass and copy"""
    if x.__class__ in SUBS_TYPES:
        # Note the explicit check for *precisely* these classes, *not* isinstance
        cls = type( 'Subs', (x.__class__,), {} )
        return cls( x )
    elif isinstance( x, list ):
        raise TypeError( """Use globalsub.PropList( mylist ) to make your list subs-compatible""" )
    return x

def subs( function, replacement=None ):
    """Replaces function in all namespaces with replacement 
    
    function -- function to replace
    replacement -- if provided, is used as the replacement object,
        otherwise a function returning None is constructed 
    
    Used to stub out functionality globally, this function uses 
    global_replace to find all references to function and replace 
    them with replacement.  Use restore( replacement ) to restore 
    function references.
    
    Note: 
    
        Only references in namespaces will be replaced, references 
        in anything other than dictionaries will not be replaced.
    
    returns replacement
    """
    _mocker_replace_ = False
    if replacement is None:
        def replacement( *args, **named ):
            return None 
        replacement.__name__ = function.__name__
    else:
        replacement = subsable( replacement )
    if function is not replacement:
        replacement.__is_subs__ = True
        replacement.original = [function,replace_filter(replacement)]
        global_replace( function, replacement )
        return replacement 
    return function

def restore( function ):
    """Restore previously subs'd function in all namespaces
    
    function -- the replacement function which was substituted 

    returns resolved function
    """
    _mocker_replace_ = False
    new,filters = resolve( function )
    if new is not function:
        global_replace( function, new, filters )
    return new

def resolve( function ):
    """Find original function from the function or subs of the function"""
    _mocker_replace_ = False
    seen = {}
    all_filters = {}
    while hasattr( function, 'original' ):
        seen[id(function)] = True 
        function,filters = function.original
        all_filters.update( filters )
        if id(function) in seen:
            log.warn( 'Seem to have created a substituation loop on %s', function)
            break
    return function,all_filters

def global_replace(remove, install, filter=None):
    """Replace object 'remove' with object 'install' on all dictionaries.
    """
    _mocker_replace_ = False
    for referrer in gc.get_referrers(remove):
        if (
            type(referrer) is dict and
            referrer.get("_mocker_replace_", True)
        ):
            for key, value in list(referrer.iteritems()):
                if value is remove:
                    if filter and id(referrer) in filter:
                        if key in filter[id(referrer)]:
                            continue # next key 
                    referrer[key] = install
def replace_filter( install ):
    """Calculate which instances should *not* be replaced
    
    Looks for the replacement (install) in namespaces, marking 
    the key values in those namespaces as not-to-be-replaced.
    """
    _mocker_replace_ = False
    blocks = {} # id(referrer): keys_to_skip
    for referrer in gc.get_referrers(install):
        if (
            type(referrer) is dict and
            referrer.get("_mocker_replace_", True)
        ):
            for key, value in list(referrer.iteritems()):
                if value is install:
                    blocks.setdefault(id(referrer),[]).append( key )
    return blocks 
