from pyramid.security import Authenticated
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from horus.interfaces import IHorusUserClass

class BaseFactory(object):
    def __init__(self, request):
        self.request = request
        self.is_root = False

class RootFactory(BaseFactory):
    @property
    def __acl__(self):
        defaultlist = [
            (Allow, 'group:admin', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view'),
        ]

        return defaultlist

    def __init__(self, request):
        super(RootFactory, self).__init__(request)
        self.is_root = True

class UserFactory(RootFactory):
    def __init__(self, request):
        self.request = request
        self.User = request.registry.getUtility(IHorusUserClass)

    def __getitem__(self, key):
        user = self.User.get_by_pk(self.request, key)

        if user:
            user.__parent__ = self
            user.__name__ = key

        return user
