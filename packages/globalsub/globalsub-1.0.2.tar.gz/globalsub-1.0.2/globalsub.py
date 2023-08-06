"""Global substitution for Python unit tests

Provides substitution in all dictionaries throughout the interpreter,
this includes references held by objects and modules.  Restores those 
references which were replaced (only), i.e. you can re-use the objects
you used as substitutions after restoring.
"""
__version__ = '1.0.2'
import gc,logging 
log = logging.getLogger(__name__)

__all__ = ['subs','restore','List']

class List( list ):
    """Use to wrap your lists so that they can be subs'd (deprecated, just pass in lists)"""

SUBS_TYPES = (str,unicode,int,long,float,tuple,complex,set,bool,)
def subsable( x ):
    """For built-in types that do not allow arbitrary attributes, subclass and copy"""
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
        _RESTORE_MAPPING[ id(replacement) ] = [function,replace_filter(replacement)]
        global_replace( function, replacement )
        return replacement 
    return function

_RESTORE_MAPPING = {
    # id(replacement): [ function, replace_filter( replacement ) ],
}

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
    while id(function) in _RESTORE_MAPPING:
        seen[id(function)] = True 
        function,filters = _RESTORE_MAPPING.pop( id(function))
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
