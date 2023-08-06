from cPickle import PicklingError
from zope.interface.declarations import ProvidesClass
from interfaces import JunkInterface

def check_importable(item):
    namespace, target = get_namespace_target(item)
    try:
        exec("from %s import %s" % (namespace, target))
        return True
    except ImportError:
        return False
    except SyntaxError:
        print 'SyntaxError'
        print dottedName, name, namespace, target, str(item)
        return False

def is_provides(item):
    return "<zope.interface.Provides object" in str(item)

def get_namespace_target(item):
    dottedName = str(item).split()[-1][:-1]
    if dottedName[0] in ('"', "'"):
        dottedName = dottedName[1:]
    if dottedName[-1] in ('"', "'"):
        dottedName = dottedName[:-1]        
    name = dottedName.split('.')
    return '.'.join(name[:-1]), name[-1]

from zope.interface.adapter import AdapterLookupBase

import pdb

def cleaner(provides, level=0):
    try:
        cleaned = _cleaner(provides, level=level)
    except RuntimeError:
        if level == 0:
            pdb.set_trace()
        else:
            raise
    return cleaned

def _cleaner(provides, level=0, tuple_type=type(())):
    """Cleans up the provides attribute, so that referenced
    classes and interfaces are removed."""
    level = level + 1
    for key, value in provides.__dict__.items():
        if key in ('_Provides__args', '__bases__', '__iro__',
                   '__sro__', 'declared'):
            new = ()
            if not type(value) is tuple_type:
                print key, value, 'is not', tuple_type
                continue
            for index in range(len(value)):
                value_ = value[index]
                if is_provides(value_):
                    if provides is value_:
                        # Why is provides instance referenced within itself?
                        new = new + (value_,)
                    else:
                        new = new + (cleaner(value_, level=level),)
                elif check_importable(value_):
                    new = new + (value_,)
                elif '__builtin__' in str(value_):
                    new = new + (value_,)
                else:
                    print 'Replacing', key, value_, 'with JunkInterface'
                    new = new + (JunkInterface,)
            setattr(provides, key, new)
        elif key == '_implied':
            for key_, value_ in value.items():
                if is_provides(key_) or is_provides(value_):
                    if is_provides(key_) and is_provides(value_):
                        del value[key_]
                        value[cleaner(key_, level=level)] = cleaner(value_, level=level)
                    elif is_provides(key_):
                        del value[key_]
                        value[cleaner(key_, level=level)] = value_
                    elif is_provides(value_):
                        value[key_] = cleaner(value_, level=level)
                elif not check_importable(key_):
                    #del value[key_]
                    value[key_] = JunkInterface
        elif key == 'dependents':
            # Do anything here?
            pass
    return provides

from zope.interface import declarations

def _normalizeargs(sequence, output = None):
    """Normalize declaration arguments

    Normalization arguments might contain Declarions, tuples, or single
    interfaces.

    Anything but individial interfaces or implements specs will be expanded.
    """
    if output is None:
        output = []

    cls = sequence.__class__
    if declarations.InterfaceClass in cls.__mro__ or \
            declarations.Implements in cls.__mro__:
        output.append(sequence)
    else:
        try:
            for v in sequence:
                _normalizeargs(v, output)
        except TypeError:
            print '_normalizeargs failed on', sequence
            return output

    return output

declarations._normalizeargs = _normalizeargs

class ALBPatch:
    def add_extendor(self, provided):
        _extendors = self._extendors
        try:
            for i in provided.__iro__:
                extendors = _extendors.get(i, ())
                _extendors[i] = (
                    [e for e in extendors if provided.isOrExtends(e)]
                    +
                    [provided]
                    +
                    [e for e in extendors if not provided.isOrExtends(e)]
                    )
        except AttributeError, value:
            print 'faking module and interface class'
            print 'provided', provided
            namespace, target_name = get_namespace_target(provided)
            class fakemodule:
                pass
            from zope.interface import Interface
            import sys
            exec("global %s" % target_name)
            exec("class %s(Interface): pass" % target_name)
            setattr(fakemodule, target_name, eval(target_name))
            sys.modules[namespace] = fakemodule

            # Get the site manager and unregister components
            # that are tied with missing interfaces.

AdapterLookupBase.add_extendor = ALBPatch.add_extendor.im_func

