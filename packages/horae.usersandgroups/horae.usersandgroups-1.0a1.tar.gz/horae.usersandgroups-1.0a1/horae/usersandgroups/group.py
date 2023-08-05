import grok

from zope.schema.fieldproperty import FieldProperty
from z3c.relationfield.interfaces import IHasRelations

from horae.core.container import Container
from horae.core.interfaces import IHorae
from horae.auth.interfaces import IGroup
from horae.search.utils import reindexSecurity

from horae.usersandgroups import interfaces


class GroupContainer(Container):
    """ A container for groups
    """
    grok.implements(interfaces.IGroupContainer)


@grok.implementer(interfaces.IGroupContainer)
@grok.adapter(IHorae)
def groupcontainer_of_holder(holder):
    """ Returns the :py:class:`GroupContainer` and if it does
        not yet exist creates one
    """
    if not 'groups' in holder:
        holder['groups'] = GroupContainer()
    return holder['groups']


class Group(grok.Model):
    """ A group
    """
    grok.implements(IGroup, IHasRelations)

    id = FieldProperty(IGroup['id'])
    name = FieldProperty(IGroup['name'])
    description = FieldProperty(IGroup['description'])
    roles = FieldProperty(IGroup['roles'])


@grok.subscribe(IGroup, grok.IObjectModifiedEvent)
def group_modified(obj, event):
    """ Reindexes security if a group has been modified
    """
    reindexSecurity()
