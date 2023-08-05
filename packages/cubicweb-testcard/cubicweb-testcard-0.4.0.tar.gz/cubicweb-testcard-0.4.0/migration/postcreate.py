# postcreate script. You could setup site properties or a workflow here for example
"""

:organization: Logilab
:copyright: 2001-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from cubes.localperms import xperm

# TestInstance workflow
tcwf = add_workflow(_('default test instance workflow'), 'TestInstance')

todo    = tcwf.add_state(_('todo'), initial=True)
succeed = tcwf.add_state(_('succeed'))
failed  = tcwf.add_state(_('failed'))

tcwf.add_transition(_('success'), todo, succeed,
                    ('managers', 'staff'), xperm('client', 'developer'))
tcwf.add_transition(_('failure'), todo, failed,
                    ('managers', 'staff'), xperm('client', 'developer'))
