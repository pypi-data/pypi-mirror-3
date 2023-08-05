"""remberme cube hooks

:organization: Logilab
:copyright: 2009-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from cubicweb.server import hook

from cubes.rememberme.authplugin import AuthCookieAuthentifier

class ServerStartupHook(hook.Hook):
    """task to cleanup expirated auth cookie entities"""
    __regid__ = 'authcookieinit'
    events = ('server_startup',)

    def __call__(self):
        # XXX use named args and inner functions to avoid referencing globals
        # which may cause reloading pb
        def cleanup_auth_cookies(repo=self.repo):
            session = repo.internal_session()
            try:
                session.execute('DELETE CWAuthCookie X WHERE X lifetime L, '
                                'X creation_date < (NOW - L)')
                session.commit()
            finally:
                session.close()
        self.repo.looping_task(60*60, cleanup_auth_cookies, self.repo)
        self.repo.system_source.add_authentifier(AuthCookieAuthentifier())
