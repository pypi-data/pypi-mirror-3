import grok

from zope.site.hooks import getSite

from horae.auth.interfaces import IGroupProvider, IUserProvider

from horae.usersandgroups import interfaces


class GroupProvider(grok.GlobalUtility):
    """ Provider for available groups
    """
    grok.implements(IGroupProvider)
    grok.name('horae.usersandgroups.groups')

    def groups(self):
        """ Returns a list of groups providing IGroup
        """
        try:
            groups = interfaces.IGroupContainer(getSite())
        except:
            return []
        return groups.objects()

    def get_group(self, id):
        """ Returns the group with the specified id or None
        """
        try:
            groups = interfaces.IGroupContainer(getSite())
        except:
            return None
        if not id in groups:
            return None
        return groups.get_object(id)


class UserProvider(grok.GlobalUtility):
    """ Provider for available users
    """
    grok.implements(IUserProvider)
    grok.name('horae.usersandgroups.users')

    def users(self):
        """ Returns a list of users providing IUser
        """
        try:
            users = interfaces.IUserContainer(getSite())
        except:
            return []
        return users.objects()

    def get_user(self, username):
        """ Returns the user with the specified username or None
        """
        try:
            users = interfaces.IUserContainer(getSite())
        except:
            return None
        if not username in users:
            return None
        return users.get_object(username)
