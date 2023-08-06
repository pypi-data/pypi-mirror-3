from zope import component
from plone.app.layout.viewlets import common
from plone.registry.interfaces import IRegistry


class BaseLineViewlet(common.ViewletBase):
    """base line viewlet"""

    def update(self):
        super(BaseLineViewlet, self).update()
        self.registry = component.queryUtility(IRegistry)
        portal = self.portal_state.portal()
        self.site_title = portal.getProperty('title')
        self.site_desc = portal.getProperty('description')

        self.baseline = u""
        if self.registry:
            try:
                self.baseline = self.registry['collective.baseline']
            except KeyError:
                pass

        if not self.baseline:
            self.baseline = self.site_desc
