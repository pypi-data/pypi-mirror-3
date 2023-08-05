"""Clean out ghosted catalog objects

Version 1.0 of collective.contentgovernance could cause catalog corruption by 
setting the default value on indexing. Setting the default value would
cause changeOwnership to be called, which in turn would trigger a re-index,
which in turn then would lead to 'ghost' entries in the portal_catalog as the
triggering indexing wasn't completed yet.

This view finds these ghosts and removes them from the catalog again. It only
needs to be run once.

"""
from zope.publisher.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class CleanupCatalogGhosts(BrowserView):
    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')._catalog
        data = catalog.data
        uids = catalog.uids
        paths = catalog.paths
        indexes = catalog.indexes.keys()
        count = 0

        for rid, uid in list(paths.items()):
            if uid in uids and uids[uid] == rid:
                # Not a ghost
                continue
            for name in indexes:
                x = catalog.getIndex(name)
                if hasattr(x, 'unindex_object'):
                    x.unindex_object(rid)
            if rid in data:
                del data[rid]
            del paths[rid]
            catalog._length.change(-1)
            count += 1

        return 'Cleared %d ghost objects from the catalog' % count
