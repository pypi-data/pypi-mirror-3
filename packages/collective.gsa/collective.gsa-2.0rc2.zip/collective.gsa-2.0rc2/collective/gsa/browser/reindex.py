from logging import getLogger
import transaction
import gc
from zope.component import getUtility, getMultiAdapter

from Products.Five import BrowserView

from collective.gsa.interfaces import IGSAQueue

logger = getLogger('collective.gsa.indexing')

class Reindex(BrowserView):
    
    def __call__(self):
        return
        catalog = getMultiAdapter( (self.context, self.request), name=u"plone_tools").catalog()
        context_url = '/'.join(self.context.getPhysicalPath())
        path = self.request.get('path',context_url)

        logger.info('Reindexing path: %s' % path)

        brains = catalog.searchResults(path = path)
        count = len(brains)
        if self.request.has_key('debug'):
            return count or 'Nothing'

        # purge utility at the begging
        queue = getUtility(IGSAQueue)
        queue.purge()
        queue = None
        indexer = getUtility(IIndexQueueProcessor, name=u"gsa")
        
        for i, brain in enumerate(brains):
            if i % 10 == 0 and i > 1:
                gc_pre = len(gc.garbage)
                pc = gc.collect()
                gc_post = len(gc.garbage)
                logger.info('Reindexing: %d out of %d (%s collected, %s, %s)' % (i,count,pc, gc_pre, gc_post))
                transaction.commit()

            obj = brain.getObject()
            try:
                indexer.index(obj)
            except MemoryError,e:
                logger.error('Retrying: %s ' % obj.absolute_url())
                try:
                    indexer.commit()
                    indexer.index(obj)
                except MemoryError,e:
                    logger.error('Memory error: %s ' % obj.absolute_url())
                
            #obj.reindexObject()
            obj = None
            del brain

        return 'reindexed %d ' % count
