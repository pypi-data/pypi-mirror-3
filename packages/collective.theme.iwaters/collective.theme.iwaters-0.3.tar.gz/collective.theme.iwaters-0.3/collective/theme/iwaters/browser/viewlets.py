from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from plone.memoize import ram

import datetime

class FooterViewletUnCached(ViewletBase):
    year = datetime.datetime.today().year
    render = ViewPageTemplateFile('footer.pt')

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def last_update(self):
        last_updates = self.portal_catalog(sort_on='modified',
                sort_order='reverse', sort_limit=1)
        return last_updates[0].modified.strftime('%Y-%m-%d')

    def update(self):
        self.year = datetime.datetime.today().year

class FooterViewlet(FooterViewletUnCached):

    def _updated_cachekey(method, self, **args):
        #once every hour is good enough
        return datetime.datetime.now().strftime('%Y%m%d%H')

    @ram.cache(_updated_cachekey)
    def last_update(self):
        return super(FooterViewlet, self).last_update()
