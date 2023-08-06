from pyramid.httpexceptions import HTTPUnauthorized, HTTPForbidden
from stucco_auth.tables import User

import logging
log = logging.getLogger(__name__)

def lookup_groups(userid, request):
    user = request.db.query(User)\
            .filter(User.username==userid).first()
    if user is not None:
        groups = map(str, user.groups)
        log.debug("%r", groups)
        return groups
    return None

def forbidden_view(request):
    """Throw a 401 if not logged in."""
    if not request.remote_user:
        return HTTPUnauthorized()
    return HTTPForbidden()

