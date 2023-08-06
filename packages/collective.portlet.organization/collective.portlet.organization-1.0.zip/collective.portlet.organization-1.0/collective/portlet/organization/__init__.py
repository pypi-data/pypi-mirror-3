from zope.i18nmessageid import MessageFactory
OrganizationPortletMessageFactory = MessageFactory('collective.portlet.organization')

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles('collective.portlet.organization: Add organization portlet',
                ('Manager', 'Site Administrator', 'Owner',))
