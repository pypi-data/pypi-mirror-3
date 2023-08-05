"""this contains the cube-specific entities' classes

:organization: Logilab
:copyright: 2001-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
from cubicweb.entities import AnyEntity

class TestInstance(AnyEntity):
    __regid__ = 'TestInstance'
    fetch_attrs = ('name',)

    @property
    def version(self):
        """project item interface"""
        return self.for_version[0]

    @property
    def project(self):
        """project item interface"""
        return self.version.project

