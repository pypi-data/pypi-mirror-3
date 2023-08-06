# Make this a Python package

import grok

def get_path(self, item, include_self=False):
    "Return the list of pages leading to this edition."
    path = []
    item = item.page
    while item is not None:
        path.append(item)
        item = item.__parent__
    path.reverse()
    if not include_self:
        del path[-1]
    del path[0]
    return path

grok.View.get_path = get_path
