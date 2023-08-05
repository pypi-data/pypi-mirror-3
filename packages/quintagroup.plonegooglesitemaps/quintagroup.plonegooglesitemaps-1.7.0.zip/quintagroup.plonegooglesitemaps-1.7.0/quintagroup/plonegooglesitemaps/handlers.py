from zope.component import adapter
from Products.CMFCore.utils import getToolByName
#from quintagroup.plonegooglesitemaps.events import AfterTransitionEvent
from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from quintagroup.plonegooglesitemaps.utils import ping_google


@adapter(IAfterTransitionEvent)
def pingGoogle(event):
    tr_id = getattr(event.transition, 'id', '')
    if not tr_id:
        # object under creation
        return 0

    object = event.object
    catalog = getToolByName(object, 'portal_catalog')

    sitemaps = [b.getObject() for b in catalog(portal_type='Sitemap')]
    if sitemaps:
        url = getToolByName(object, 'portal_url')
        plone_home = url.getPortalObject().absolute_url()
        wftrans_name = "%s#%s" % (event.workflow.id, tr_id)
        obj_ptype = object.portal_type
        for sm in sitemaps:
            if wftrans_name in sm.getPingTransitions() \
               and obj_ptype in sm.getPortalTypes():
                ping_google(plone_home, sm.id)
    return 0
