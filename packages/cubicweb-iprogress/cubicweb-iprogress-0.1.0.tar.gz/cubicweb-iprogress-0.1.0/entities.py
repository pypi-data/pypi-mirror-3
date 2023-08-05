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
"""cubicweb-iprogress adapters"""

from cubicweb.view import EntityAdapter

class IProgressAdapter(EntityAdapter):
    """something that has a cost, a state and a progression.

    You should at least override progress_info an in_progress methods on
    concrete implementations.
    """
    __regid__ = 'IProgress'
    __abstract__ = True

    @property
    def cost(self):
        """the total cost"""
        return self.progress_info()['estimated']

    @property
    def revised_cost(self):
        return self.progress_info().get('estimatedcorrected', self.cost)

    @property
    def done(self):
        """what is already done"""
        return self.progress_info()['done']

    @property
    def todo(self):
        """what remains to be done"""
        return self.progress_info()['todo']

    def progress_info(self):
        """returns a dictionary describing progress/estimated cost of the
        version.

        - mandatory keys are (''estimated', 'done', 'todo')

        - optional keys are ('notestimated', 'notestimatedcorrected',
          'estimatedcorrected')

        'noestimated' and 'notestimatedcorrected' should default to 0
        'estimatedcorrected' should default to 'estimated'
        """
        raise NotImplementedError

    def finished(self):
        """returns True if status is finished"""
        return not self.in_progress()

    def in_progress(self):
        """returns True if status is not finished"""
        raise NotImplementedError

    def progress(self):
        """returns the % progress of the task item"""
        try:
            return 100. * self.done / self.revised_cost
        except ZeroDivisionError:
            # total cost is 0 : if everything was estimated, task is completed
            if self.progress_info().get('notestimated'):
                return 0.
            return 100

    def progress_class(self):
        return ''


class IMileStoneAdapter(IProgressAdapter):
    __regid__ = 'IMileStone'
    __abstract__ = True

    parent_type = None # specify main task's type

    def get_main_task(self):
        """returns the main ITask entity"""
        raise NotImplementedError

    def initial_prevision_date(self):
        """returns the initial expected end of the milestone"""
        raise NotImplementedError

    def eta_date(self):
        """returns expected date of completion based on what remains
        to be done
        """
        raise NotImplementedError

    def completion_date(self):
        """returns date on which the subtask has been completed"""
        raise NotImplementedError

    def contractors(self):
        """returns the list of persons supposed to work on this task"""
        raise NotImplementedError

