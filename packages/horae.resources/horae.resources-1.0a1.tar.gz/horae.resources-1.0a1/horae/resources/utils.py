from horae.auth.utils import getUser
from horae.core.utils import getRequest


def resourceAvailable(resource, user=None):
    """ Checks if the given resource is available for the given
        or otherwise the current user
    """
    if user is None:
        try:
            request = getRequest()
            user = getUser(request.principal.id)
        except:
            pass
    if (not resource.groups and not resource.users) or \
       (resource.users and user.username in resource.users) or \
       (user is not None and resource.user == user.username):
        return True
    if user is None:
        return None
    for group in user.groups:
        if resource.groups and group.id in resource.groups:
            return True
    return False
