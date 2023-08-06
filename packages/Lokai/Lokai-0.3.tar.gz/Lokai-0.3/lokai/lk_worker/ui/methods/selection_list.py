# Name:      lokai/lk_worker/ui/methods/selection_list.py
# Purpose:   Provides a base for restful paged lists of results
# Copyright: 2011: Database Associates Ltd.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
#    See the License for the specific language governing permissions and
#    limitations under the License.

#-----------------------------------------------------------------------

""" Provides a set of lines laid out visually as a table. Columns can
    be sorted (one column only at any time).

    All functions are accessed by links instead of buttons.

    The table is single select only, as selecting a line (by clicking
    on the link) is expected to go straight to view detail. This
    behaviour could be modified if required.

    The selection list is requested by a url that points to the
    selection list display code and gives a page to be displayed. This
    means that the navigation buttons can be links.

    The selection list url can have optional data that indicates, for
    example, a required sort field and sort order.

    The detail display is requested by a url that points to the detail
    display code and gives a (possibly composite) id for the target to
    be displayed.

"""
#-----------------------------------------------------------------------

import json

import lokai.tool_box.tb_common.notification as notify
from lokai.tool_box.tb_forms.form import Form
from lokai.tool_box.tb_forms.widget import (RowWidget,
                                      CompositeWidget,
                                      DisplayOnlyWidget)

from lokai.lk_worker.ui.link_widget import TableWidget

#-----------------------------------------------------------------------

class SelectionList(Form):

    def __init__(self, request, object_reference, data_object, **kwargs):
        self.current_target = request.derived_locals['current_target']
        self.node_perm = perm = request.derived_locals['permissions']
        self.request = request
        self.obj_ref = object_reference
        self.obj = data_object
        self.new_child = request.args.get('down')

        self.required_permission = kwargs.get('perm', 'nde_tasks')

        filter_data = request.args.get('filter')
        self.selection_filter = {}
        if filter_data:
            self.selection_filter = json.loads(filter_data)
        self._get_display_columns()
        self.heading_map = {}
        for i in range(len(self.headings)):
            self.heading_map[self.headings[i][0]] = i
        self.start_row = None
        self.chunksize = kwargs.get('chunksize', 10)

        self._interpret_perms()
        
        Form.__init__(self, request_object=request,
                      use_tokens=False,
                      **kwargs)

        # Defer building the form so that derived classes can do
        # __init__ actions after this one.
        self.build_form_needed = True
        
    def _capture_data(self, do_query=False):
        """ Prepare the list navigation and build the list data set.

            Optionally - do not run the actual query.
        """
        self.set_start_point(self.request)
        self.identify_sort()
        if do_query:
            self.run_query()
        self.build_vars()
        
    #-------------------------------------------------------------------

    # Overloadable

    def _interpret_perms(self):
        """ Look at permissions to see if we are limited in any way in
            what we can do.

            As the basis for a selection disply, this default version
            does nothing particularly useful, but it establishes the
            principle.
        """
        assert self.required_permission
        self.can_edit = (self.obj_ref and
                    self.obj_ref != '**new**' and
                    self.node_perm.test_permit(self.required_permission, 'edit'))
        self.can_add = (self.obj_ref == '**new**' and
                   self.node_perm.test_permit(self.required_permission, 'add'))

    def _get_display_columns(self):
        """ set self.headings with an appropriate set of columns
            acording to whatever logic might apply. Typically this might
            depend on user permisions.
        """
        self.headings = []

    def _add_to_query(self, query):
        """ Add another table to the basic node query. Do this by
            overloading.

            Remember that the base query contains the node and
            associated activity data.

            This method is called in run_query. If you overload
            run_query you may choose not to use _add_to_query.
        """
        return query

    def run_query(self):
        """ Build the data set to be displayed, and find a total size
            of the data set.

            self.u_set <- a list of rows returned from the
                database. The first row of this set must correspond to
                the first row of the current page, and the length must
                be no more then chunksize.

            self.u_set_len <- the total number of rows in the data
                that would be returned if no limits were applied.
        """
        raise NotImplementedError('This method must be overloaded and '
                                  'populate self.u_set from a result set')

    def build_navigation(self):
        """ Put together btf_pages and associated btf_enabled to form
            the navigaion header.

            Put together the links for the column headings based on
            self.headings

            self.btf_pages <- list, one entry per navigation link, of
                tuples. (name, target, url parts, optional query)

            self.btf_enabled <- tuple or list, one entry per
                navigation link, true if link is supposed to work.

            self.columns <- list, one entry per column to be
                displayed, of tuples. (name, text, target, query)
        """
        raise NotImplementedError
        

    def build_row_display(self, u_row, widget):
        """ Populate the display widgets for a single row.

            u_row is a row extracted from u_set

            widget is a composite widget - normally this is an empty
                RowWidget, but that is not essential.

            This method uses widget.add to place one widget for each
            heading (or whatever else is needed.
        """
        raise NotImplementedError
        
        
    def build_pre_form(self):
        """ Add anything to the start of the form
        """
        pass
        
    def build_pre_tw_form(self):
        """Add anything to the start of the form inside the tablewidget
        """
        pass
        
    def build_post_form(self):
        """ Add anything to the end of the form - this can include
            adding items to the self.table_widget
        
            e.g. Add in the submit row so that it goes at the end

                 self.table_widget.add(ButtonRow, 'actions')
                 button_row = self.table_widget.get_widget('actions')
                 button_row.add(DisplayOnlyWidget, 'nothing')
                 button_row.add(SubmitWidget, 'detail',
                                'Show selected')
                 if self.perm.test_permit(self.keys['perm'], 'add'):
                     button_row.add(SubmitWidget, 'add',
                                    'Add new')
        """
        pass

    def build_row_widget(self, widget):
        """ Build the display widgets for a single row.

            :widget: CompositeWidget - defines the row. Build the row
                widget by adding column widgets correspondoing to the
                headings.
        """
        pass

    #-------------------------------------------------------------------

    # Things below here are reasonably general

    #-------------------------------------------------------------------

    def identify_sort(self):
        """ Evaluate the headings for the order by part of query
        """
        if (self.current_col is None and
            self.keys.get('base_order', None) not in [None, '']):
            self.current_col = self.keys['base_order']
        self.sort_column = None
        self.has_select = False
        for heading in self.headings:
            if isinstance(heading, (list, tuple)) and len(heading) > 1:
                if heading[0] in ['select', 'select_one']:
                    self.has_select = heading[0]
                elif self.current_col is None:
                    # Choose the first column that is not a 'select'
                    # as a default
                    # 
                    self.current_col = heading[0]
                if self.current_col == heading[0]:
                    # We are sorting on this column
                    self.sort_column = heading[0]
                    break # no need to look any further - we can do the query.

    def build_vars(self):
        """ Build variables and values for determining where we are.

            Runs immediately after run_query and before any form
            building.
        """
        self.table_rows = min(self.chunksize-1, len(self.u_set))
        self.end_row = min(self.start_row+self.chunksize - 1,
                           self.start_row+len(self.u_set) -1)

    def build_form(self):
        """ Put together the parts for a form. Most of this is calling
            overloadables.
        """
        #
        # Capture defered action so it is not repeated
        if not self.build_form_needed:
            return
        self.build_form_needed = False

        # Get the data we are going to display
        self._capture_data(True)

        # Now to the form proper
        self.build_pre_form()
        self.build_navigation()
        self.add(TableWidget, self.keys['formname'],
                 title      = self.keys.get('title', 'List'),
                 fieldset   = {},
                 tableset   = {'heading_set' : self.columns,
                               'btf_pages': self.btf_pages,
                               'btf_enabled' : self.btf_enabled
                              },
                )
        self.table_widget = self.get_widget(self.keys['formname'])
        self.build_pre_tw_form()
        self.table_widget.add(CompositeWidget, 'body',
                     fieldset   = {}
                    )
        self.build_post_form()
        self.build_list()
        
    def build_list(self):
        """ Build a set of empty row widgets and a pagination place
            holder.
        """
        body = self.table_widget.get_widget('body')        
        for row in range(len(self.u_set)):
            body.add(RowWidget, str(row))
            widget = body.get_widget(str(row))
            self.build_row_widget(widget)
            
        # A widget to indicate pagination/results
        body.add(RowWidget, 'pagination')
        w = body.get_widget('pagination')
        w.add(DisplayOnlyWidget, 'pt')
        pages = int(float(len(self.u_set)) / float(self.chunksize))
    
    def build_data(self):
        """ Populate the table/list widgets with data from the search.
        
            Includes adding the info string detailing results
            displayed
        """
        # Get the form ...
        self.build_form()

        # Now do the work
        body = self.table_widget.get_widget('body')
        for row in range(len(self.u_set)):
            u_row = self.u_set[row]
            w = body.get_widget(str(row))
            self.build_row_display(u_row, w)
        # Populate the pagination/results information
        w = body.get_widget('pagination')
        info_str = ' &nbsp; No results found'
        if len(self.u_set) > 0:
            if self.start_row == self.end_row:
                info_str = ' &nbsp; Showing result %s of %s' % (
                    str(self.start_row+1),
                    str(self.u_set_len))
            else:
                info_str = ' &nbsp; Showing results %s to %s of %s' % (
                    str(self.start_row+1),
                    str(self.end_row+1),
                    str(self.u_set_len))
        w.get_widget('pt').set_value(info_str)
        jtp = w.get_widget('jump_to_page')
        if jtp:
            jtp.set_value('')
    
    def set_start_point(self, request):
        start = request.args.get('row', '')
        if isinstance(start, type(0)):
            self.start_row = start
        else:
            start = start.strip()
            if start.isdigit():
                self.start_row = int(start)
            else:
                self.start_row = 0
        self.current_col = request.args.get('order', None)
        self.flow = request.args.get('flow', None)

    def render(self):
        # Make sure the form has been built, at least
        self.build_form()
        return Form.render(self)

#-----------------------------------------------------------------------
