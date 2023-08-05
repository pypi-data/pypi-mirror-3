import grok

from zope import component, interface
from zope.i18n import translate
from zope.formlib.interfaces import WidgetInputError
from megrok import navigation

from horae.layout import layout
from horae.layout import objects
from horae.layout.interfaces import IGlobalManageMenu, IObjectTableActionsProvider
from horae.core.interfaces import IHorae, ITextIdManager
from horae.auth.interfaces import IGroup, IUser
from horae.auth import utils

from horae.usersandgroups import _
from horae.usersandgroups.group import Group
from horae.usersandgroups.user import User
from horae.usersandgroups import interfaces

# Groups


class GroupsOverview(objects.ObjectOverview):
    """ Overview of all available groups
    """
    grok.context(IHorae)
    grok.require('horae.ManageGroups')
    grok.name('groups-overview')
    navigation.sitemenuitem(IGlobalManageMenu, _(u'Groups'))

    label = _(u'Groups')
    add_label = _(u'Add group')
    columns = [('name', _(u'Name')), ('description', _(u'Description')), ('actions', u'')]
    container_iface = interfaces.IGroupContainer

    def row_factory(self, object, columns, request):
        row = super(GroupsOverview, self).row_factory(object, columns, request)
        row.update({
            'name': object.name,
            'description': object.description})
        return row

    def add(self):
        return self.url(self.container) + '/add-group'


class AddGroup(layout.AddForm):
    """ Add form for groups
    """
    grok.context(interfaces.IGroupContainer)
    grok.require('horae.ManageGroups')
    grok.name('add-group')

    form_fields = grok.AutoFields(IGroup).omit('id')

    def object_type(self):
        return _(u'Group')

    def cancel_url(self):
        return self.url(self.context.__parent__) + '/groups-overview'

    def next_url(self, obj=None):
        return self.cancel_url()

    def create(self, **data):
        idmanager = component.getUtility(ITextIdManager)
        group = Group()
        id = unicode(idmanager.idFromName(self.context, u'group.' + data['name']))
        try:
            group.id = id
        except interface.Invalid:
            i = 1
            while True:
                try:
                    group.id = '%s-%s' % (id, i)
                    break
                except interface.Invalid:
                    i += 1
        return group

    def add(self, obj):
        self.context.add_object(obj)


class EditGroup(objects.EditObject):
    """ Edit form of a group
    """
    grok.context(interfaces.IGroupContainer)
    grok.require('horae.ManageGroups')
    grok.name('edit-group')

    form_fields = grok.AutoFields(IGroup).omit('id')
    overview = 'groups-overview'
    dynamic_fields = False

    def object_type(self):
        return _(u'Group')


class DeleteGroup(objects.DeleteObject):
    """ Delete form of a group
    """
    grok.context(interfaces.IGroupContainer)
    grok.require('horae.ManageGroups')
    grok.name('delete-group')

    overview = 'groups-overview'

    def object_type(self):
        return _(u'Group')


class GroupActionsProvider(grok.MultiAdapter):
    """ Action provider for groups adding buttons to edit and delete
        the group
    """
    grok.adapts(IGroup, GroupsOverview)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.usersandgroups.objecttableactions.group')

    def __init__(self, context, view):
        self.context = context
        self.view = view

    def actions(self, request):
        container_url = self.view.url(self.view.container)
        actions = [{'url': container_url + '/edit-group?id=' + str(self.context.id),
                    'label': translate(_(u'Edit'), context=request),
                    'cssClass': ''},
                   {'url': container_url + '/delete-group?id=' + str(self.context.id),
                    'label': translate(_(u'Delete'), context=request),
                    'cssClass': 'button-destructive delete'}]
        return actions


# Users


class UsersOverview(objects.ObjectOverview):
    """ Overview of all available users
    """
    grok.context(IHorae)
    grok.require('horae.ManageUsers')
    grok.name('users-overview')
    navigation.sitemenuitem(IGlobalManageMenu, _(u'Users'))

    label = _(u'Users')
    add_label = _(u'Add user')
    columns = [('username', _(u'Username')), ('name', _(u'Name')), ('actions', u'')]
    container_iface = interfaces.IUserContainer

    def row_factory(self, object, columns, request):
        row = super(UsersOverview, self).row_factory(object, columns, request)
        row.update({
            'username': object.username,
            'name': object.name})
        return row

    def add(self):
        return self.url(self.container) + '/add-user'


class UniqueUsernameValidationMixin(object):

    def validate(self, action, data):
        errors = super(UniqueUsernameValidationMixin, self).validate(action, data)
        existing = utils.getUser(data['username'])
        if existing is not None:
            errors.append(WidgetInputError('username', self.form_fields['username'].field.title, _(u'The username is already in use, please specify another one')))
        return errors


class AddUser(UniqueUsernameValidationMixin, layout.AddForm):
    """ Add form for users
    """
    grok.context(interfaces.IUserContainer)
    grok.require('horae.ManageUsers')
    grok.name('add-user')

    form_fields = grok.AutoFields(IUser)

    def object_type(self):
        return _(u'User')

    def cancel_url(self):
        return self.url(self.context.__parent__) + '/users-overview'

    def next_url(self, obj=None):
        return self.cancel_url()

    def create(self, **data):
        user = User()
        user.username = data['username']
        return user

    def add(self, obj):
        self.context.add_object(obj)


class EditUser(objects.EditObject):
    """ Edit form of a user
    """
    grok.context(interfaces.IUserContainer)
    grok.require('horae.ManageUsers')
    grok.name('edit-user')

    form_fields = grok.AutoFields(IUser).omit('password', 'username')
    overview = 'users-overview'
    id_attr = 'username'
    dynamic_fields = False

    def object_type(self):
        return _(u'User')


class DeleteUser(objects.DeleteObject):
    """ Delete form of a user
    """
    grok.context(interfaces.IUserContainer)
    grok.require('horae.ManageUsers')
    grok.name('delete-user')

    overview = 'users-overview'
    id_attr = 'username'

    def object_type(self):
        return _(u'User')

    def delete(self):
        self.context.del_object(self.object.username)


class UserActionsProvider(grok.MultiAdapter):
    """ Action provider for users adding buttons to edit and delete
        the user
    """
    grok.adapts(IUser, UsersOverview)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.usersandgroups.objecttableactions.user')

    def __init__(self, context, view):
        self.context = context
        self.view = view

    def actions(self, request):
        container_url = self.view.url(self.view.container)
        actions = [{'url': container_url + '/edit-user?id=' + str(self.context.username),
                    'label': translate(_(u'Edit'), context=request),
                    'cssClass': ''},
                   {'url': container_url + '/delete-user?id=' + str(self.context.username),
                    'label': translate(_(u'Delete'), context=request),
                    'cssClass': 'button-destructive delete'}]
        return actions
