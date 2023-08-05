from persistent.list import PersistentList
import AccessControl
from Globals import InitializeClass

View = 'View'
Manage = 'Manage'

class CAG:

    # Should only be changed once and then before __init__.
    CAG_prefix = 'cag_storage_'
    CAG_archive_limit = 500
    CAG_last_archive = 0

    security = AccessControl.ClassSecurityInfo()

    def __init__(self, id, title):
        setattr(self, self.CAG_prefix + str(self.CAG_last_archive), PersistentList())
    
    security.declareProtected(View, 'CAG_append')
    def CAG_append(self, item):
        # No __doc__ string, so it can't be accessed TTW

        active_archive = getattr(self, self.CAG_prefix + str(self.CAG_last_archive))
        active_archive.append(item)
        if len(active_archive) > self.CAG_archive_limit:
            last = self.CAG_last_archive = self.CAG_last_archive + 1
            archive_id = self.CAG_prefix + str(last)
            setattr(self, archive_id, PersistentList())

    security.declareProtected(View, 'CAG_get_numbered_item')
    def CAG_get_numbered_item(self, archive, index):
        # No __doc__ string, so it can't be accessed TTW

        #"""Returns a numbered item."""
        return getattr(self, self.CAG_prefix + str(archive))[index]

    security.declareProtected(View, 'CAG_get_since')
    def CAG_get_since(self, since_function, numbered=False):
        # No __doc__ string, so it can't be accessed TTW

        #"""Returns entries on and after since_function returns true."""
        entries = self.CAG_get(count=100000000, numbered=numbered)
        for index in range(len(entries)):
            if since_function(entries[index]):
                return entries[index:]
        else:
            return []

    security.declareProtected(View, 'CAG_get_numbered_since')
    def CAG_get_numbered_since(self, since_function):
        # No __doc__ string, so it can't be accessed TTW

        #"""Returns entries on and after since_function returns true."""
        return self.CAG_get_since(since_function, numbered=True)

    security.declareProtected(View, 'CAG_get_numbered')
    def CAG_get_numbered(self, count=300, context_archive=None, context_index=None):
        # No __doc__ string, so it can't be accessed TTW

        #"""Gets the numbered count (archive id, index, item) of items."""
        return self.CAG_get(count=count, numbered=True, context_archive=context_archive,
                            context_index=context_index)

    security.declareProtected(View, 'CAG_get') 
    def CAG_get(self, count=300, numbered=False, context_archive=None, context_index=None):
        # No __doc__ string, so it can't be accessed TTW

        #"""Get 'count' number of last items added, return first-last-added."""

        # What happens if an item is appended while we're fetching?
        #
        # Could be optimized to only look in relevant archives
        #
        # count either return the last count items, or with
        # context_archive and context_index defined, the
        # count/2 items before and after context_index.
        last_archive = self.CAG_last_archive
        items = []
        while len(items) < count:
            if last_archive is -1:
                break
            try:
                prior_items = list(getattr(self, self.CAG_prefix + str(last_archive)))
                if numbered:
                    prior_items_ = []
                    for index in range(len(prior_items)):
                        prior_items[index] = ((last_archive, index, prior_items[index]))
                prior_items.extend(items)
                items = prior_items
                last_archive = last_archive - 1
            except AttributeError:
                break
        if context_archive is not None:
            context = self.CAG_archive_limit * context_archive
            context = context + context_index
            start = max(0, context - (count/2))
            stop = context + (count/2)
            return items[start:stop]
        else:
            items = items[-count:]
            return items

InitializeClass(CAG)
