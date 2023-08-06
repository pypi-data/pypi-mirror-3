import transaction

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable

class Update(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = []
        def updateTranslatedPaths(obj, path=None):
            if (base_hasattr(obj, 'indexObject') and
                safe_callable(obj.indexObject) and
                base_hasattr(obj, 'getPhysicalPath') and
                safe_callable(obj.getPhysicalPath)):
                try:
                    path = '/'.join(obj.getPhysicalPath())
                    catalog._catalog.updateTanslatedPaths(obj, path)
                    results.append('Updated %s' % path)
                    transaction.commit()
                except:
                    pass
        context.ZopeFindAndApply(context, search_sub=True, apply_func=updateTranslatedPaths)
        return u'Successfully updated the IDs of the following objects:\n'+('='*54)+'\n\n' + '\n'.join(results)
