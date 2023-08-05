from zope.interface import Interface

from zope.interface import implements
from zope.component import getMultiAdapter
from zope import schema
from zope.formlib import form

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
##from plone.app.vocabularies.catalog import SearchableTextSourceBinder


from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

##from ely.portlets.image import ImagePortletMessageFactory as _
from my315ok.portlet.logo import LogoPortletMessageFactory as _
##from ely.portlets.image.widget import ImageWidget
from my315ok.portlet.logo.widget import ImageWidget

class ILogoPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

   
    imgsrc = schema.TextLine(title=_(u"target URI"),
                             description=_(u"the URI of the resouce images view"),
                             required=False
                             
                             )
    image = schema.Field(title=_(u'Image field'),
                         description=_(u"upload for Add or replace image"),
                         required=False
                       )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ILogoPortlet)
    assignment_context_path = None
    imgsrc = None
    image = None
    

    def __init__(self,
                 assignment_context_path = None,imgsrc=None,
                 image=None):
        self.imgsrc = imgsrc
        self.image = image
        self.assignment_context_path = assignment_context_path
        

    @property
    def title(self):
       
        return _(u'Logo Portlet')


class Renderer(base.Renderer):
    """Portlet renderer.
    """

    render = ViewPageTemplateFile('logoportlet.pt')

    @property
    @memoize
    def image_tag(self):
        state=getMultiAdapter((self.context, self.request),
                                  name="plone_portal_state")
        portal=state.portal()
        ptitle = state.portal_title()
        imgsrc = self.data.imgsrc
        
        if imgsrc:
            return "<img  class='%s' src='%s' alt='%s' />" % \
                   ("hack-png",imgsrc,ptitle)
            
            
        elif self.data.image:                                   
            assignment_url = \
                    portal.unrestrictedTraverse(
                self.data.assignment_context_path).absolute_url()
            width = self.data.image.width
            height = self.data.image.height
            return "<img  class='%s' src='%s/%s/@@image' width='%s' height='%s' alt='%s' />" % \
                   ("hack-png",
		    assignment_url,
                    self.data.__name__,
                    str(width),
                    str(height),
                    ptitle)
        return None

    @property
    @memoize
    def site_url(self):
        
        state=getMultiAdapter((self.context, self.request),
                              name="plone_portal_state")
        portal_url=state.navigation_root_url()
        
        return portal_url
    
       
   

class AddForm(base.AddForm):
    """Portlet add form.
    """
    form_fields = form.Fields(ILogoPortlet)
    form_fields['image'].custom_widget = ImageWidget
    

    def create(self, data):
        assignment_context_path = \
                    '/'.join(self.context.__parent__.getPhysicalPath())
        return Assignment(assignment_context_path=assignment_context_path,
                          **data)

class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(ILogoPortlet)
    form_fields['image'].custom_widget = ImageWidget
   
