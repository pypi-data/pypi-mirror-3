from zope.component import getUtilitiesFor
from zope.event import notify
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
from zope.interface import Interface, implements
from zope import schema
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
from plone.app.users.browser.register import (
    CantChoosePasswordWidget,
    RegistrationForm)
from plone.app.workflow.interfaces import ISharingPageRole
from plone.app.layout.viewlets.common import ViewletBase

from collective.local.adduser.event import UserLocallyAdded

PMF = MessageFactory('plone')
_ = MessageFactory('adduser')


class IAddUserSchema(Interface):

    roles = schema.List(
        title=_(u'label_assign_permissions',
                default=u'Assign the following permissions:'),
        description=u'',
        required=False,
        default=['Reader'],
        value_type=schema.Choice(vocabulary='LocalRoles'))


class LocalRolesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        portal_membership = getToolByName(context, 'portal_membership')

        terms = []

        for name, utility in getUtilitiesFor(ISharingPageRole):
            permission = utility.required_permission
            if permission is None or portal_membership.checkPermission(permission, context):
                terms.append(SimpleTerm(name, name, utility.title))

        terms.sort(key=lambda x: normalizeString(
            translate(x.title, context=context.REQUEST)))
        return SimpleVocabulary(terms)


class AddUserInSharing(ViewletBase):

    def update(self):
        pass

    def render(self):
        return u"""
<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery('#new-user-link').prepOverlay({subtype: 'ajax'});
    });
</script>
<p><a href="%s" id="new-user-link">%s</a></p>""" % (
                '%s/@@add-new-user' % self.context.absolute_url(),
                translate(PMF(u"heading_add_user_form", default=u"Add New User"),
                    context=self.request))


class AddUserForm(RegistrationForm):

    @property
    def form_fields(self):
        defaultFields = super(AddUserForm, self).form_fields
        if not defaultFields:
            return []
        defaultFields = defaultFields.omit('password', 'password_ctl')
        defaultFields['mail_me'].custom_widget = CantChoosePasswordWidget

        allFields = defaultFields + form.Fields(IAddUserSchema)
        allFields['roles'].custom_widget = MultiCheckBoxVocabularyWidget
        return allFields


    @form.action(PMF(u'label_register', default=u'Register'),
                             validator='validate_registration', name=u'register')
    def action_join(self, action, data):
        super(AddUserForm, self).handle_join_success(data)
        user_id = data['username']
        if 'roles' in data.keys():
            self.context.manage_addLocalRoles(user_id, data['roles'])
            self.context.reindexObjectSecurity()
            notify(UserLocallyAdded(self.context, user_id, data['roles']))
        IStatusMessage(self.request).addStatusMessage(
            PMF(u"User added."), type='info')
        self.request.response.redirect(
                self.context.absolute_url() + "/@@sharing")
