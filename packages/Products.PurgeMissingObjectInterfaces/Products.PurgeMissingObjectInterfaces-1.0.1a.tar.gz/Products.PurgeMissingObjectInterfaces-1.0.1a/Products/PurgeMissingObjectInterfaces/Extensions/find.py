from Products.PurgeMissingObjectInterfaces import cleaner, check_importable
import pprint, StringIO

def find(self, string='p4a', target='plone'):
    context = self[target]
    strings = string.split(',')
    count = 0
    cleaned = []
    result = [[context.id, context]]
    result.extend(self.ZopeFind(self, search_sub=True))
    for id_, object_ in result:
        has_missing_interfaces = r_find(object_, strings=strings)
        if has_missing_interfaces:
            new = cleaner(object_.__provides__)
            object_._p_changed = True
            count += 1
            cleaned.append('/'.join(object_.getPhysicalPath()))
    return ("Cleaned %s objects" % count) + '\n\n' + '\n'.join(cleaned)

def r_find(self, strings=[]):
    """Finds objects with missing marker interfaces."""
    try:
        provides = self.__provides__
    except AttributeError:
        return False
    import pprint, StringIO
    file = StringIO.StringIO()
    pprint.pprint(provides.__dict__, file, depth=100000)
    value = file.getvalue()
    found = []
    for string in strings:
        if string in value:
            found.append(string)
    return found
