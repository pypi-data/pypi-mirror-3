# cube's specific schema
"""

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
from yams.buildobjs import EntityType, RelationDefinition, Int, Interval
from cubicweb.schema import ERQLExpression, RRQLExpression


class CWAuthCookie(EntityType):
    __permissions__ = {
        'read': ('managers', ERQLExpression('X owned_by U')),
        'add': ('managers', 'users'),
        'update': ('managers', 'owners'),
        'delete': ('managers', 'owners'),
        }

    magicnumber = Int()
    lifetime = Interval()


class auth_cookie_for_user(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U identity O', 'O')),
        'delete': ('managers', RRQLExpression('U identity O', 'O')),
        }

    subject = 'CWAuthCookie'
    object = 'CWUser'

    cardinality = '1*'
    composite = 'object'

    inlined = True
