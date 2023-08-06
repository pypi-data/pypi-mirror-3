# Old semi-broken code

def adapter_cleaner(adapter):
    changed = False
    for adapter_set in adapter['_adapters']:
        for key, value in adapter_set.items():
            if not check_importable(key):
                #del adapter_set[key]
                adapter_set[key] = JunkInterface
                changed = True
    for key, value in adapter['_provided'].items():
        if not check_importable(key):
            #del adapter['_provided'][key]
            adapter['_provided'] = JunkInterface
            changed = True
    for subscriber_set in adapter['_subscribers']:
        for key, value in subscriber_set.items():
            if not check_importable(key):
                #del subscriber_set[key]
                subscriber_set[key] = JunkInterface
                changed = True
    return adapter


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

from ZODB.serialize import ObjectWriter

def _dump(self, classmeta, state):
    # Copied from ZODB/serialize.py
    self._file.seek(0)
    self._p.clear_memo()
    self._p.dump(classmeta)
    try:
        self._p.dump(state)
    except PicklingError, exception_object:
        # Handling except on error text, new one
        if exception_object.args[0].startswith("Can't pickle <class"):
            raise
            from Products.PurgeMissingObjectInterfaces import cleaner
            provides = state['__provides__'] = cleaner(state['__provides__'])
            self._p.dump(state)
        else:
            raise
    self._file.truncate()
    return self._file.getvalue()

ObjectWriter._dump = _dump


from ZODB import serialize

class ObjectReaderPatch:

    def setGhostState(self, obj, pickle):
        state = self.getState(pickle)
        try:
            obj.__setstate__(state)
        except AttributeError:
            raise
            print 'cleaning state..'
            print state.keys()
            obj.__setstate__(adapter_cleaner(state))

#serialize.ObjectReader.setGhostState = ObjectReaderPatch.setGhostState.im_func

#from ZODB.Connection import Connection
#old_setstate = Connection._setstate.im_func

import pprint, cStringIO, transaction

#class ConnectionPatch:
#
#    def _setstate(self, obj):
#        old_setstate(self, obj)
#
#        if hasattr(obj, '_adapters') and hasattr(obj, '_provided') and\
#                hasattr(obj, '_subscribers'):
#            print 'cleaning adapter object..'
#            transaction.begin()
#            adapter_cleaner_object(obj)
#            obj._p_changed = True
#            transaction.commit()

#Connection._setstate = ConnectionPatch._setstate.im_func

from zope.interface.adapter import AdapterLookupBase, LookupBasePy

old_uncached_lookup = AdapterLookupBase._uncached_lookup

def _uncached_lookup(self, required, provided, name=u'', default=None):
    try:
        return old_uncached_lookup(self, required, provided, name=name)
    except AttributeError:
        print 'attributeerror in uncached', self, required, provided, name
        for registry in self._registry.ro:
            adapter_cleaner_object(registry)
        return old_uncached_lookup(self, required, provided, name=name, default=default)


AdapterLookupBase._uncached_lookup = _uncached_lookup
LookupBasePy = _uncached_lookup
