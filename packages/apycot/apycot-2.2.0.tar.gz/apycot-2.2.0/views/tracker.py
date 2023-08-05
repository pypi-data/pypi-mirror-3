"""this module contains some stuff to integrate the apycot cube into jpl

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import is_instance
from cubicweb.view import EntityView
from cubicweb.web import uicfg

_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('Project', 'has_apycot_environment', '*'), 'attributes')

class ProjectTestResultsTab(EntityView):
    """display project's documentation"""
    __regid__ = title = _('apycottestresults_tab')
    __select__ = is_instance('Project')

    def cell_call(self, row, col):
        rset = self._cw.execute(
            'Any T,TC,T,TB,TST,TET,TF, TS ORDERBY TST DESC WHERE '
            'T status TS, T using_config TC, T branch TB, '
            'T starttime TST, T endtime TET, T log_file TF?, '
            'T using_environment PE, P has_apycot_environment PE, '
            'P eid %(p)s', {'p': self.cw_rset[row][col]})
        self.wview('apycot.te.summarytable', rset, 'noresult', showpe=False)


# class VersionTestResultsVComponent(component.EntityVComponent):
#     """display the latest tests execution results"""
#     __regid__ = 'apycottestresults'
#     __select__ = component.EntityVComponent.__select__ & is_instance('Version')

#     context = 'navcontentbottom'
#     rtype = 'has_apycot_environment'
#     target = 'object'
#     title = _('Latest test results')
#     order = 11

#     def cell_call(self, row, col, **kwargs):
#         entity = self.cw_rset.get_entity(row, col)
#         configsrset = entity.related('has_apycot_environment')
#         if not configsrset:
#             return
#         self.wview('summary', configsrset, title=self._cw._(self.title))


try:
    from cubes.tracker.views.project import ProjectPrimaryView
except ImportError:
    pass
else:
    if 'apycottestresults_tab' not in ProjectPrimaryView.tabs:
        ProjectPrimaryView.tabs.append('apycottestresults_tab')
