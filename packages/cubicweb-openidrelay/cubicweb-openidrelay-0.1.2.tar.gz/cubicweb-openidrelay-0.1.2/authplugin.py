"""
:organization: Logilab
:copyright: 2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from cubicweb import AuthenticationError
from cubicweb.server.sources import native

class OpenIDAuthentifier(native.BaseAuthentifier):
    """return CWUser eid for the given login/openid pair"""
    auth_rql = 'Any U WHERE U is CWUser, U login %(login)s, U openid %(openid)s'

    def authenticate(self, session, login, **kwargs):
        """return CWUser eid for the given login (coming from x-remote-user
        http headers) if this account is defined in this source,
        else raise `AuthenticationError`
        """
        session.debug('authentication by %s', self.__class__.__name__)
        try:
            args = kwargs.copy()
            args.update({'login': login})
            rset = session.execute(self.auth_rql, args)
            if rset:
                return rset[0][0]
        except Exception, exc:
            session.debug('authentication failure (%s)', exc)
            pass
        raise AuthenticationError('user is not registered')
