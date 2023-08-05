# copyright 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""Specific views for entities implementing IProgress/IMileStone"""

__docformat__ = "restructuredtext en"
_ = unicode

from math import floor

from logilab.mtconverter import xml_escape

from cubicweb.utils import make_uid
from cubicweb.selectors import adaptable
from cubicweb.schema import display_name
from cubicweb.view import EntityView
from cubicweb.web.views import tableview


def state_cell(w, entity):
    w(xml_escape(entity.cw_adapt_to('IWorkflowable').printable_state))

def eta_date_cell(w, entity):
    imilestone = entity.cw_adapt_to('IMileStone')
    req = entity._cw
    if imilestone.finished():
        formated_date = req.format_date(imilestone.completion_date())
    else:
        formated_date = req.format_date(imilestone.initial_prevision_date())
        if imilestone.in_progress():
            eta_date = req.format_date(imilestone.eta_date())
            if eta_date:
                if formated_date:
                    formated_date += u' (%s %s)' % (req._('expected:'), eta_date)
                else:
                    formated_date = u'%s %s' % (req._('expected:'), eta_date)
        w(formated_date)

def todo_by_cell(w, entity):
    imilestone = entity.cw_adapt_to('IMileStone')
    w(u', '.join(p.view('outofcontext') for p in imilestone.contractors()))

def cost_cell(w, entity):
    req = entity._cw
    pinfo = entity.cw_adapt_to('IMileStone').progress_info()
    totalcost = pinfo.get('estimatedcorrected', pinfo['estimated'])
    missing = pinfo.get('notestimatedcorrected', pinfo.get('notestimated', 0))
    costdescr = []
    if missing:
        # XXX: link to unestimated entities
        costdescr.append(req._('%s not estimated') % missing)
    estimated = pinfo['estimated']
    if estimated and estimated != totalcost:
        costdescr.append(req._('initial estimation %s') % estimated)
    if costdescr:
        w(u'%s (%s)' % (totalcost, ', '.join(costdescr)))
    else:
        w(unicode(totalcost))

def progress_cell(w, entity):
    entity.view('progressbar', w=w)


class ProgressTableView(tableview.EntityTableView):
    """The progress table view is able to display progress information
    of any object implement IMileStone.

    By default it is composed of 7 columns : parent task, milestone, state,
    estimated date, cost, progressbar, and todo_by

    As :class:`EntityTableView` a `columns` class attribute lets you remove or
    reorder some of those columns.
    """

    __regid__ = 'progress_table_view'
    __select__ = adaptable('IMileStone')

    title = _('task progression')
    layout_id = 'imilestone_table_layout'
    columns = ('project', 'milestone', _('state'), _('eta_date'),
               _('cost'), _('progress'), _('todo_by'))

    class ProjectColRenderer(tableview.EntityTableColRenderer):
        def render_header(self, w):
            sample = self.entity(0)
            w(display_name(self._cw, sample.cw_adapt_to('IMileStone').parent_type))
        def render_entity(self, w, entity):
            project = entity.cw_adapt_to('IMileStone').get_main_task()
            project.view('incontext', w=w)
        def entity_sortvalue(self, entity):
            return entity.cw_adapt_to('IMileStone').get_main_task().sortvalue()

    class MileStoneColRenderer(tableview.MainEntityColRenderer):
        def render_header(self, w):
            sample = self.entity(0)
            w(display_name(self._cw, sample.__regid__))

    column_renderers = {
        'project': ProjectColRenderer(),
        'milestone': MileStoneColRenderer(),
        'state': tableview.EntityTableColRenderer(renderfunc=state_cell),
        'eta_date': tableview.EntityTableColRenderer(renderfunc=eta_date_cell),
        'cost': tableview.EntityTableColRenderer(renderfunc=cost_cell),
        'progress': tableview.EntityTableColRenderer(renderfunc=progress_cell),
        'todo_by': tableview.EntityTableColRenderer(renderfunc=todo_by_cell),
        }


class InContextProgressTableView(ProgressTableView):
    """this views redirects to ``progress_table_view`` but removes
    the ``project`` column
    """
    __regid__ = 'ic_progress_table_view'

    def call(self, columns=None):
        if columns is None:
            view = self._cw.vreg['views'].select('progress_table_view', self._cw,
                                                 rset=self.cw_rset)
            columns = list(view.columns)
            self.column_renderers = view.column_renderers
        try:
            columns.remove('project')
        except ValueError:
            self.info('[ic_progress_table_view] could not remove project from columns')
        super(InContextProgressTableView, self).call(columns=columns)


class ProgressTableLayout(tableview.TableLayout):
    __regid__ = 'imilestone_table_layout'
    cssclass = 'progress'
    needs_css = ('cubes.iprogress.css',)

    def row_attributes(self, rownum):
        attrs = super(ProgressTableLayout, self).row_attributes(rownum)
        entity = self.view.entity(rownum)
        cssclass = entity.cw_adapt_to('IMileStone').progress_class()
        attrs['class'] += cssclass
        return attrs


class ProgressBarView(EntityView):
    """displays a progress bar"""
    __regid__ = 'progressbar'
    __select__ = adaptable('IProgress')

    title = _('progress bar')

    precision = 0.1
    red_threshold = 1.1
    orange_threshold = 1.05
    yellow_threshold = 1

    @classmethod
    def overrun(cls, iprogress):
        done = iprogress.done or 0
        todo = iprogress.todo or 0
        budget = iprogress.revised_cost or 0
        if done + todo > budget:
            overrun = done + todo - budget
        else:
            overrun = 0
        if overrun < cls.precision:
            overrun = 0
        return overrun

    @classmethod
    def overrun_percentage(cls, iprogress):
        budget = iprogress.revised_cost or 0
        if budget == 0:
            return 0
        return cls.overrun(iprogress) * 100. / budget

    def cell_call(self, row, col):
        self._cw.add_css('cubes.iprogress.css')
        self._cw.add_js('cubes.iprogress.js')
        entity = self.cw_rset.get_entity(row, col)
        iprogress = entity.cw_adapt_to('IProgress')
        done = iprogress.done or 0
        todo = iprogress.todo or 0
        budget = iprogress.revised_cost or 0
        if budget == 0:
            pourcent = 100
        else:
            pourcent = done*100./budget
        if pourcent > 100.1:
            color = 'red'
        elif todo+done > self.red_threshold*budget:
            color = 'red'
        elif todo+done > self.orange_threshold*budget:
            color = 'orange'
        elif todo+done > self.yellow_threshold*budget:
            color = 'yellow'
        else:
            color = 'green'
        if pourcent < 0:
            pourcent = 0

        if floor(done) == done or done>100:
            done_str = '%i' % done
        else:
            done_str = '%.1f' % done
        if floor(budget) == budget or budget>100:
            budget_str = '%i' % budget
        else:
            budget_str = '%.1f' % budget

        title = u'%s/%s = %i%%' % (done_str, budget_str, pourcent)
        short_title = title
        overrunpercent = self.overrun_percentage(iprogress)
        if overrunpercent:
            overrun = self.overrun(iprogress)
            title += u' overrun +%sj (+%i%%)' % (overrun, overrunpercent)
            if floor(overrun) == overrun or overrun > 100:
                short_title += u' +%i' % overrun
            else:
                short_title += u' +%.1f' % overrun
        # write bars
        maxi = max(done+todo, budget)
        if maxi == 0:
            maxi = 1
        cid = make_uid('progress_bar')
        self._cw.html_headers.add_onload(
            'draw_progressbar("canvas%s", %i, %i, %i, "%s");' %
            (cid, int(100.*done/maxi), int(100.*(done+todo)/maxi),
             int(100.*budget/maxi), color))
        self.w(u'%s<br/>'
               u'<canvas class="progressbar" id="canvas%s" width="100" height="10"></canvas>'
               % (xml_escape(short_title), cid))

def registration_callback(vreg):
    oldclasses = (ProgressTableView, InContextProgressTableView, ProgressBarView)
    vreg.register_all(globals().values(), __name__, oldclasses)
    # clear registry so that if cw bw compat views are in, they are kicked out
    # first
    for cls in oldclasses:
        vreg.register(cls, clear=True)
