# Old broken code

def complete_dump(self, file, count=0, been_dumped=[]):
    if self in been_dumped: return
    count = count + 1
    if hasattr(self, '__dict__'):
        pprint.pprint(self.__dict__, file, depth=1)
        for key, value in self.__dict__.items():
            complete_dump(value, file, count=count)
    else:
        pprint.pprint(self, file, depth=1)
    been_dumped.append(self)

def dump(self):
    from zope.component._api import getSiteManager
    sm = getSiteManager(self.plone)
    sm._p_changed = True
    putters = []
    file = StringIO.StringIO()
    #pprint.pprint(sm.__dict__, file, depth=1)
    #pprint.pprint(sm.__dict__['adapters'].__dict__['ro'][1].__dict__, file)
    #value = file.getvalue()
    complete_dump(sm, file)
    return file.getvalue()
    utility = sm._utility_registrations
    for key, value in utility.items():
        if not check_importable(key[0]):
            del utility[key]
        value = str(value)[1:]
        if value.startswith('<class') or value.startswith('<InterfaceClass'):
            if not check_importable(value):
                del utility[key]
    return utility

