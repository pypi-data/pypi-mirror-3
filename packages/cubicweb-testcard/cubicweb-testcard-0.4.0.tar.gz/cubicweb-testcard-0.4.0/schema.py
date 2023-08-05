"""
test cards schema

:organization: Logilab
:copyright: 2001-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
from yams.reader import context
from yams.buildobjs import RelationDefinition, String
from cubicweb.schema import WorkflowableEntityType
from cubes.localperms import oexpr, sexpr


class TestInstance(WorkflowableEntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (), # handled by hook
        'update': ('managers',),
        'delete': ('managers',),
        }
    ## attributes
    # name size constraint should be the same as Card's title
    name  = String(required=True, fulltextindexed=True, maxsize=256)


class test_case_of(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', oexpr('developer', 'client'),),
        'delete': ('managers', 'staff', oexpr('developer', 'client'),),
        }
    subject = 'Card'
    object = 'Project'
    cardinality = '?*'
    description = _('specify that a card is describing a test for a project')


class test_case_for(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', oexpr('developer', 'client'),),
        'delete': ('managers', 'staff', oexpr('developer', 'client'),),
        }
    subject = 'Card'
    object = 'Ticket'
    cardinality = '?*'
    description = _('specify that a card is describing a test for a particular story')


class for_version(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (), # handled by hook
        'delete': ('managers', 'users',), # will need delete perm on TestInstance
        }
    subject = 'TestInstance'
    object = 'Version'
    cardinality = '1*'
    composite = 'object'
    inlined = True


class generate_bug(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }
    subject = 'TestInstance'
    object = 'Ticket'
    description = _('link to a bug encountered while passing the test')


class instance_of(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (), # handled by hook
        'delete': ('managers', 'users',),
        }
    subject = 'TestInstance'
    object = 'Card'
    cardinality = '1*'
    composite = 'object'
    inlined = True


if 'Comment' in context.defined:
    class comments(RelationDefinition):
        subject = 'Comment'
        object = 'TestInstance'
        cardinality = '1*'
        composite = 'object'
