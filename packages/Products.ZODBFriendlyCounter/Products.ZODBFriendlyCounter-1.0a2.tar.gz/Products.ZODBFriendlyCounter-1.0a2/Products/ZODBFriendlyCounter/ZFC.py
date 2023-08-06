"""Package with counter"""

def manage_add_zfc(self, id='counter', title='', REQUEST=None):
    """Adds an ZFC instance to self."""
    self._setObject(id, ZFC(id, title))
    #if REQUEST is not None:
    return self.manage_main(self, self.REQUEST)

#from App.special_dtml import DTMLFile
#manage_add_zfc_form = DTMLFile('add_form', globals())

import thread, os

global counters
counters = {}

def get_unique(persistent_counter,
               # Do not alter this, at least not
               # after having instances of the
               # class.
               COUNT_BEFORE_STORING = 100):
    counter_key = (os.getpid(), thread.get_ident())
    global counters
    try:
        counter = counters[counter_key]
    except KeyError:
        try:
            counter = persistent_counter._counters[counter_key] + COUNT_BEFORE_STORING
            persistent_counter._counter_skips[counter_key] += 1
        except KeyError:
            persistent_counter._counters[counter_key] = 0
            counter = 0
    counter += 1
    counters[counter_key] = counter
    if counter > (persistent_counter._counters.get(counter_key, 0) + COUNT_BEFORE_STORING):
        persistent_counter._counters[counter_key] = counter
    return str(hash(counter_key)) + '_' + str(counter)

from Globals import Persistent, InitializeClass
from OFS.SimpleItem import SimpleItem
from Persistence.mapping import PersistentMapping
from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.Permissions import view as View, view_management_screens

class ZFC(Persistent, SimpleItem):
    """Class that provides unique ids."""

    meta_type = 'ZODBFriendlyCounter'

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)
    
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._counters = PersistentMapping()
        self._counter_skips = PersistentMapping()

    def __call__(self):
        "Returns a unique value."
        return get_unique(self)

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        "Increments counter, returns value."
        return self.__call__()

    security.declareProtected(view_management_screens, 'debug')
    def debug(self):
        "Returns raw data for debugging/checking"
        return str(self._counters) + '\n\n' + str(self._counter_skips)
    
    def manage_workspace(self):
        "No management possible"
        return "No management possible, except ./debug"

InitializeClass(ZFC)
