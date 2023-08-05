import grok

from zope import component
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.fieldproperty import FieldProperty
from zope.app.intid.interfaces import IIntIds
from zope.app.authentication.interfaces import IPasswordManager
from z3c.relationfield import RelationValue
from z3c.relationfield.interfaces import IHasRelations

from horae.core.interfaces import IHorae
from horae.core.container import Container
from horae.search.utils import reindexSecurity

from horae.usersandgroups import interfaces


class UserContainer(Container):
    """ A container for users
    """
    grok.implements(interfaces.IUserContainer)

    def add_object(self, obj):
        """ Adds a new object and returns the generated id
        """
        self._last = obj
        self[str(obj.username)] = obj
        return str(obj.username)


@grok.implementer(interfaces.IUserContainer)
@grok.adapter(IHorae)
def usercontainer_of_holder(holder):
    """ Returns the :py:class:`UserContainer` and if it does
        not yet exist creates one
    """
    if not 'users' in holder:
        holder['users'] = UserContainer()
    return holder['users']


class User(grok.Model):
    """ A user implementation using zc.relations to reference the groups
    """
    grok.implements(interfaces.IRelationUser, IHasRelations)

    username = FieldProperty(interfaces.IRelationUser['username'])
    name = FieldProperty(interfaces.IRelationUser['name'])
    email = FieldProperty(interfaces.IRelationUser['email'])
    roles = FieldProperty(interfaces.IRelationUser['roles'])

    encoded_password = None
    groups_rel = None

    def set_groups(self, groups):
        intids = component.getUtility(IIntIds)
        self.groups_rel = [RelationValue(intids.queryId(obj)) for obj in groups]
        notify(ObjectModifiedEvent(self))

    def get_groups(self):
        if self.groups_rel is None:
            return None
        return [group.to_object for group in self.groups_rel]
    groups = property(get_groups, set_groups)

    def set_password(self, password):
        passwordmanager = component.getUtility(IPasswordManager, 'SHA1')
        self.encoded_password = passwordmanager.encodePassword(password)

    def get_password(self):
        return None
    password = property(get_password, set_password)

    def checkPassword(self, password):
        """ Checks the provided password
        """
        passwordmanager = component.getUtility(IPasswordManager, 'SHA1')
        return passwordmanager.checkPassword(self.encoded_password, password)


@grok.subscribe(interfaces.IRelationUser, grok.IObjectModifiedEvent)
def user_modified(obj, event):
    """ Reindexes security if a user has been modified
    """
    reindexSecurity()
