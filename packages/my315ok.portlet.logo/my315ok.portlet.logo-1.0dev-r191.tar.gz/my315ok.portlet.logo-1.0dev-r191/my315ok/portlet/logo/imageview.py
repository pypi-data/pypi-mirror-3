from Acquisition import aq_inner
from zope.interface import implements

from Products.Five.browser import BrowserView

from my315ok.portlet.logo.interfaces import IImagePortletImageView

class ImageView(BrowserView):
    '''
    View the image field of the image portlet. We steal header details
    from zope.app.file.browser.file and adapt it to use the dublin
    core implementation that the Image object here has.
    '''

    implements(IImagePortletImageView)

    def __call__(self):
        context = aq_inner(self.context)
        image = context.image
        return image.index_html(self.request, self.request.response)
