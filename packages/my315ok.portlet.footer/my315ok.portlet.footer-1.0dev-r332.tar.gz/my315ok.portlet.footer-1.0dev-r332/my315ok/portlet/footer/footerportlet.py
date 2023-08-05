from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from my315ok.portlet.footer import FooterPortletMessageFactory as _
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget


class IFooterPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    text = schema.Text(
        title=_(u"Text"),
        description=_(u"The text to render"),
        required=True)
    
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IFooterPortlet)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field
    text = u""

    def __init__(self,text=u""):
        self.text = text
        

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Footer portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('footerportlet.pt')


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IFooterPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    label = _(u"title_add_static_portlet",
              default=u"Add static text portlet")
    description = _(u"description_static_portlet",
                    default=u"A portlet which can display static HTML text.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IFooterPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    label = _(u"title_edit_static_portlet",
              default=u"Edit static text portlet")
    description = _(u"description_static_portlet",
                    default=u"A portlet which can display static HTML text.")
