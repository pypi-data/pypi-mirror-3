from DateTime import DateTime
from quintagroup.plonegooglesitemaps.browser.commonview \
    import CommonSitemapView, implements, ISitemapView


class SitemapView(CommonSitemapView):
    """
    Sitemap browser view
    """
    implements(ISitemapView)

    additional_maps = (
        ('modification_date', lambda x: DateTime(x.ModificationDate).HTML4()),
    )

    def getFilteredObjects(self):
        return self.portal_catalog(
            path=self.search_path,
            portal_type=self.context.getPortalTypes(),
            review_state=self.context.getStates()
            )
