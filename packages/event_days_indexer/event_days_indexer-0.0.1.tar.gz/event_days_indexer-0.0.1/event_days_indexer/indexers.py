
# register this as documented at
#   http://collective-docs.readthedocs.org/en/latest/searching_and_indexing/indexing.html#custom-index-methods


from plone.indexer.decorator import indexer
from Products.ATContentTypes.interfaces.event import IATEvent
from Products.ATContentTypes.utils import DT2dt


@indexer(IATEvent)
def event_days(context, **kw):
    start = DT2dt(context.start())
    end = DT2dt(context.end())
    delta = end - start
    if delta.days <= 1:
        return True
    else:
        return False
    #return delta.days
