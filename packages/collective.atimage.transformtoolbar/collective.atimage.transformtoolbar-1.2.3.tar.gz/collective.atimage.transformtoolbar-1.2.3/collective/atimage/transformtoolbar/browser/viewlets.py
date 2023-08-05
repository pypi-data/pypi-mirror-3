from zope.component import queryMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common
from collective.atimage.transformtoolbar.interfaces import ITransformToolbarLayer

class TransformToolbarViewlet(common.ViewletBase):
    """ Viewlet to display the icon-toolbar with transformations for ATImage and ATNewsItem
    """
    
    index = ViewPageTemplateFile('templates/toolbar.pt')
   
    def available(self):
        context = self.context
        if not ITransformToolbarLayer.providedBy(self.request):
            # Product is not installed
            return False
        elif not queryMultiAdapter((context, self.request), name='transform'):
            # Object is not transformable
            return False
        elif context.getField('image').get_size(context) == 0:
            # Object has no image
            return False
        else:
            # PIL is not available
            if not hasattr(context, 'hasPIL'):
                return False
            elif not context.hasPIL():
                return False
                
            return len(self.context.getTransformMap())

