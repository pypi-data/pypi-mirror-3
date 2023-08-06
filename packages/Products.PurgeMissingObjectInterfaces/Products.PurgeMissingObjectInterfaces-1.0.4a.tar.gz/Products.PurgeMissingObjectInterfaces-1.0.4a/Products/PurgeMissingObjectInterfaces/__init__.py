from cPickle import PicklingError
from zope.interface.declarations import ProvidesClass
from interfaces import JunkInterface
from FakeZopeInterface import FakeZopeInterface


def is_provides(item):
    return "<zope.interface.Provides object" in str(item)

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
    """Cleans up the provides attribute, so that referenced broken
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
                elif FakeZopeInterface.check_importable(value_):
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
                elif not FakeZopeInterface.check_importable(key_):
                    #del value[key_]
                    value[key_] = JunkInterface
        elif key == 'dependents':
            # Do anything here?
            pass

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
            FakeZopeInterface.fake_module_and_interface(provided)

            # Get the site manager and unregister components
            # that are tied with missing interfaces.

    def init_extendors(self):
        self._extendors = {}
        try:
            for p in self._registry._provided:
                self.add_extendor(p)
        except AttributeError, value:
            import traceback
            print 'attributeerror in init_extendor', value
            traceback.print_stack()

AdapterLookupBase.add_extendor = ALBPatch.add_extendor.im_func
AdapterLookupBase.init_extendors = ALBPatch.init_extendors.im_func

from ZODB import serialize

def _dump(self, classmeta, state):
    # Copied from ZODB/serialize.py
    self._file.seek(0)
    self._p.clear_memo()
    self._p.dump(classmeta)
    try:
        self._p.dump(state)
    except PicklingError, exception_object:
        # Handling except on error text, new one
        exception_argument = exception_object.args[0]
        if exception_argument.startswith("Can't pickle <class"):
            print 'exception in _dump', exception_argument
            if 'not the same object' in exception_argument:
                pass
                #import pdb
                #pdb.set_trace()
            from Products.PurgeMissingObjectInterfaces import cleaner
            try:
                #provides = state['__provides__'] =
                #state should be modified in-place
                cleaner(state['__provides__'])
                self._p.dump(state)
            except KeyError:
                for x in range(100):
                    # Work it until it works, create classes and modules
                    x = exception_argument
                    x = x[x.find('<')+1:x.find('>')].split()[1]
                    FakeZopeInterface.fake_module_and_interface(x)
                    try:
                        self._p.dump(state)
                        break
                    except PicklingError, value:
                        print 'passing on picklingerror in PurgeMissingObjectInterfaces', value
        else:
            raise
    self._file.truncate()
    return self._file.getvalue()

serialize.ObjectWriter._dump = _dump

def adapter_cleaner(adapter):
    changed = False
    for adapter_set in adapter['_adapters']:
        for key, value in adapter_set.items():
            if not FakeZopeInterface.check_importable(key):
                #del adapter_set[key]
                adapter_set[key] = JunkInterface
                changed = True
    for key, value in adapter['_provided'].items():
        if not FakeZopeInterface.check_importable(key):
            #del adapter['_provided'][key]
            adapter['_provided'] = JunkInterface
            changed = True
    for subscriber_set in adapter['_subscribers']:
        for key, value in subscriber_set.items():
            if not FakeZopeInterface.check_importable(key):
                #del subscriber_set[key]
                subscriber_set[key] = JunkInterface
                changed = True
    return adapter

from cStringIO import StringIO
import pprint

def create_sio_file():
    return StringIO()

def adapter_cleaner_object(adapter):
    changed = False
    for adapter_set in adapter._adapters:
        for key, value in adapter_set.items():
            if not check_importable(key):
                #del adapter_set[key]
                adapter_set[key] = JunkInterface
                changed = True
    for key, value in adapter._provided.items():
        if not check_importable(key):
            #del adapter._provided[key]
            adapter['_provided'] = JunkInterface
            changed = True
    for subscriber_set in adapter._subscribers:
        for key, value in subscriber_set.items():
            if not check_importable(key):
                #del subscriber_set[key]
                subscriber_set[key] = JunkInterface
                changed = True
    adapter._p_changed = True
    return adapter

class ObjectReaderPatch:

    def setGhostState(self, obj, pickle):
        state = self.getState(pickle)
        try:
            obj.__setstate__(state)
        except AttributeError, value:
            print 'attributeerror', (value, obj)
            print 'cleaning state..'
            print state.keys()
            adapter_cleaner(state)
            obj.__setstate__(state)
            #except KeyError, arguments:
            #    unpickler = self._get_unpickler(pickle)
            #    meta_state = unpickler.load()
            #    raise KeyError, str((state, obj, pickle, meta_state))

serialize.ObjectReader.setGhostState = ObjectReaderPatch.setGhostState.im_func
