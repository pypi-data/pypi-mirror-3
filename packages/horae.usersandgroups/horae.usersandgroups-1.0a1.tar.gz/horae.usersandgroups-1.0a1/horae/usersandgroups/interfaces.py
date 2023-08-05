from z3c.relationfield import RelationList

from horae.core.interfaces import IContainer
from horae.auth.interfaces import IUser


class IGroupContainer(IContainer):
    """ A container for groups
    """


class IRelationUser(IUser):
    """ A user implementation using zc.relations to reference the groups
    """

    groups_rel = RelationList()


class IUserContainer(IContainer):
    """ A container for users
    """
