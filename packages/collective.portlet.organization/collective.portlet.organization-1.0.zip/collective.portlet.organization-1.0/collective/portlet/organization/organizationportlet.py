from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# TODO: If you require i18n translation for any of your schema fields below,
# uncomment the following to import your package MessageFactory
from collective.portlet.organization import OrganizationPortletMessageFactory as _


class IOrganizationPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    name = schema.TextLine(title=_(u"Name"),
                           description=_(u"The organization name"),
                           required=True)
    description = schema.Text(title=_(u"Description"),
                              description=_(u"A short description of the organization"),
                              required=False)

    street = schema.TextLine(title=_(u"Address: Street"),
                                     required=False)
    postalcode = schema.TextLine(title=_(u"Address: Postal code"),
                                     required=False)
    locality = schema.TextLine(title=_(u"Address: Locality"),
                                     required=False)

    telephone = schema.TextLine(title=_(u"Telephone number"),
                                required=False)
    faxnumber = schema.TextLine(title=_(u"Fax number"),
                                required=False)
    email = schema.TextLine(title=_(u"EMail address"),
                            required=False)
    url = schema.URI(title=_(u"URL"),
                     required=False)
    logo = schema.URI(title=_(u"Logo URL"),
                      required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IOrganizationPortlet)

    name = u""
    description = u""
    street = u""
    postalcode = u""
    locality = u""
    telephone = u""
    faxnumber = u""
    email = u""
    url = u""
    logo = u""

    def __init__(self,
                 name=u"",
                 description=u"",
                 street=u"",
                 postalcode=u"",
                 locality=u"",
                 telephone=u"",
                 faxnumber=u"",
                 email=u"",
                 url=u"",
                 logo=u""):
        self.name = name
        self.description = description
        self.street = street
        self.postalcode = postalcode
        self.locality = locality
        self.telephone = telephone
        self.faxnumber = faxnumber
        self.email = email
        self.url = url
        self.logo = logo

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.name


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('organizationportlet.pt')

    def has_address(self):
        return self.data.street or \
            self.data.postalcode or \
            self.data.locality

    def has_contact(self):
        return self.data.telephone or \
            self.data.email or \
            self.data.faxnumber


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IOrganizationPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IOrganizationPortlet)
