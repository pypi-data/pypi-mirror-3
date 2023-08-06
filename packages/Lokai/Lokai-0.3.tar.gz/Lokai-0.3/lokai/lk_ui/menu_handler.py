# Name:      lokai/lk_ui/menu_handler.py
# Purpose:   Draws dynamic menu
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

import copy
from types import StringTypes

from werkzeug import html

import lokai.tool_box.tb_common.configuration as config
import lokai.tool_box.tb_common.notification as notify
from lokai.tool_box.tb_common.import_helpers import get_module_attribute

#-----------------------------------------------------------------------

class MenuHandler(object):
    """ Builds a menu and provides a render method.

        The menu is built from the config file using 'menu_publisher'
        config items within each application block.  The config item
        may point to an attribute of a module, or to a module
        containing the default attribute 'menu_builder'. Where this
        attribute is found, it is used to build the menu.

        The attribute may be a list, or a callable that returns a
        list. The callable is called with the request, and the vaules
        extracted from the URL.

        The menu handler object is built dynamically for each response
        that needs a menu. This allows the menu to be constructed
        according to context.
        
        Additional items may be added (or even removed) using direct
        calls to menuHandler().process_submenu([...])

        The menu list is a list of menu items, each of which may in
        turn contain a list of menu items as children. The menu item
        looks like this:

        'action' : string, optional with value 'delete' to remove
            item, otherwise taken as an 'add' process. Delete calls
            use 'title' to determine the node to remove from
            parent. This only of interest for elements passed in
            through menuHandler().process_submenu(...)
                   
        'parent' : [], list of titles to parent. This is only of
            interest for elements passed in through
            menuHandler().process_submenu(...) and allows the element
            to be placed as a child to an existing element.
         
        'position' : int, the ordering for the item within its
            peers. Default 999.
     
        'title' : string, the displayed text.
         
        'link' : string url, the url that the menu item points
            to. This is optional if the menu element has children.
                              
        'permission' : permission set, a set of data suited to
            permision processing. It must be non-empty to force
            permission processing.
         
        'permission_tester' : callable, function that can be used to
            process the permissions. The function receives the
            permission set, and the request (which includes the vaules
            extracted from the URL). It returns True or False.

        'image' : string url, points to an image.

        'children' : [{....}, {....}]}, {....}] )
         
        'callback' : callable, a function that can add or remove menu
            items according to context. The function receives the
            menuHandler instance, which includes the request and the
            vaules extracted from the URL, plus all other keyword
            items in the menu entry that contains the callback. For a
            callback, therefore, the items in the menu entry are
            specific to the callback's expectations and do not
            necessarily include any of the other items listed here.

    The order of processing is:

        Build the basic menu tree from all the menuItem instances.

        Process callbacks

        Trim the menu by processing permissions and removing empty
        branches.

        Sort according to positions.
        
"""

    def __init__(self, request):
        self.request = request
        self.menu_list = []
        self.callbacks = {}
        self._build_base_menu()
        self._format = 'plain'
        self.current = None

    def _build_base_menu(self):
         for name, block in config.get_global_config().iteritems():
             if 'menu_publisher' in block:
                 menu = get_module_attribute(block['menu_publisher'],
                                            'menu_builder')
                 if callable(menu):
                     # Exists as a function
                     self.process_submenu(menu(self.request))
                 else:
                     # Exists as a variable
                     # deepcopy module.menuItems to avoid globals
                     self.process_submenu(menu)

    def process_submenu(self, sub_list):
        """ Take each list item and conditionally add it to the menu """
        sub_list_copy = copy.deepcopy(sub_list)
        for sub in sub_list_copy:
            action = sub.get('action', 'add')
            if action == 'delete':
                # Remove the item
                self.remove_item(sub)
            else:
                # Add the list
                self.add_item(sub)

    def add_item(self, item):
        """ Add a menu item to the menu. """
        assert(item)
        callback = item.get('callback', None)
        if callback:
            # A callback function
            if not callback in self.callbacks.keys():
                # Remove surplus parts
                for k in ['action', 'callback']:
                    if item.get(k, None):
                        del item[k]
                self.callbacks[callback] = item
        else:
            # A node
            node = self.get_node(item.get('parent', None))
            for node_item in node:
                if node_item.get('title', '') == item.get('title', ''):
                    # Another node exists with this title at this level
                    if 'link' not in node_item or 'link' not in item:
                        # Must be different things
                        node.append(item)
                    elif ('link' not in node_item and
                          'link' not in item and
                          node_item.get('position') != item.get('position')):
                        # Two similar groups at different priorities
                        node.append(item)
                    elif node_item.get('link') == item.get('link'):
                        new_kids = item.get('children')
                        if new_kids:
                            if not 'children' in node_item:
                                node_item['children'] = new_kids
                            else:
                                link_set = [
                                    e['link'] for e in node_item['children']
                                    if 'link' in e]
                                for candidate in new_kids:
                                    if not candidate.get('link') in link_set: 
                                        node_item['children'].append(candidate)
                        node_item['position'] = min(
                            node_item.get('position', 999),
                            item.get('position', 000))
                    return
            node.append(item)
    
    def remove_item(self, item):
        """ Remove a menu item (and all its children) from the menu """
        callback = item.get('callback', None)
        if callback:
            # A callback
            if callback in self.callbacks.keys():
                del self.callbacks[callback]
        else:
            # A node
            node = self.get_node(item.get('parent', None))
            # As we only remove one item we can iterate forward
            for node_item in node:
                if node_item.get('title', None) == item.get('title', None):
                    node.remove(node_item)
                    break
        
    def get_node(self, parent_list=None):
        """ return the furthest node of self.menu_list as indicated by
            the passed parent_list.

            The search gives up when it can go no further. It is
            guaranteed to return a node, even if there is no exact
            match to the given parents.
            """
        node = self.menu_list
        if parent_list in [None, '', 'root', []]:
            return node
        if isinstance(parent_list, StringTypes):
            parent_list = [parent_list]
        if isinstance(parent_list, (list, tuple)):
            # We have a parent list... e.g. ['Administration', 'Roles']
            for parent in parent_list:
                for node_item in node:
                    title = node_item.get('title', None)
                    if title == parent:
                        if not node_item.get('children', None):
                            node_item['children'] = []
                        node = node_item['children']
                        break
        return node
    
    def render(self):
        """ Build the menu out of the various parts, trim it and
            return some html.
        """
        # Determine where the page is
        self._where_am_i(self.menu_list)
        # Process any defined callback functions
        self._process_callbacks()
        # Reduce the list(s) based on permissions
        self._reduce_under_permissions(self.menu_list)
        # Further reduce based on link values and children
        self._remove_dangling_elements(self.menu_list)
        # Set any missing parents
        self._identify_parents(self.menu_list)
        # Sort each level of the menu based on the 'position'
        self._sort_menu(self.menu_list)
        # Output the remaining items in the required format
        return self.render_html(self.menu_list)

    def render_html(self, menu_list, current_page=None):
        """ Return a simple menu

            This could be overridden for other formats.

            :menu_list: is whatever has been built, truncated or
                otherwise manipluted. The function is called
                recursively, so menu list amy also be a set of
                children.

            :current_page: is a list of menu titles that identifies
                the menu item that corresponds to the page being
                displayed (if we know it, and we can't be sure that we
                do). This means we can format that current item
                dfferently.
        """
        full_ret = ''
        if current_page is None:
            current_page = self.current[2]
        item_row = []
        for element in menu_list:
            # Determine if item should be shown
            if self.element_is_open(element):
                # Output the item.
                attribs = {}
                title_str = element.get('title', '')
                if title_str:
                    title_str = title_str.strip()
                else:
                    title_str = ''
                attribs['class'] = 'left_menu_normal'
                title_block = html.span(html(title_str) if title_str else '&nbsp;',
                                        **{'class': 'left_menu_normal'})
                if len(current_page) > 0 and title_str == current_page[0]:
                    attribs['class'] = 'left_menu_active'
                    if len(current_page) == 1:
                        title_block = (
                            html.span(html(title_str) if title_str else '&nbsp;',
                                      **{'class': 'left_menu_active'}))
                    current_page = current_page[1:]
                link = element.get('link', None)
                image = element.get('image', None)
                image_block = ''
                if image not in [None, '']:
                    image_block = html.img(src="%s" % str(image))
                if link in [None, '']:
                    m_block = '%s%s' % (image_block, title_block,)
                else:
                    link_str = str(link)
                    m_block = html.a("%s%s" % (image_block, title_block),
                                     href = link_str)

                children = element.get('children', None)
                if children:
                    child_block = self.render_html(children, current_page)
                    m_block = '\n'.join([m_block, child_block])
                item_row.append(html.li(m_block, **attribs))

        if item_row:
            full_ret = html.div(html.ul('\n'.join(item_row)),
                                style = "padding-left:8px") 
        return full_ret
        
    def _where_am_i(self, menu_list, best_guess=None):
        """ Recurse the list(s) and best guess from url where we are

            Builds self.current.

            self.current = [score, item, parent]

                score = length of url that matches where we are.

                item = menu element that we have reached.

                parent = [], list of parent titles.
        """
        if not best_guess:
            best_guess = []
        if not hasattr(self, 'current') \
           or not isinstance(self.current, (list)) \
           or len(self.current) < 3:
            self.current = [0, None, best_guess] # [score, item, parent]
        if isinstance(menu_list, list):
            for element in menu_list:
                # Determine a score
                current_guess = best_guess+[element.get('title', 'unknown')]
                url = element.get('link', None)
                if url:
                    # Does the url appear in the link browser_url?
                    browser_url = self.request.url
                    if browser_url.find(url) > -1:
                        if len(url) > self.current[0]:
                            self.current = [len(url),
                                            element,
                                            current_guess]
                children = element.get('children', None)
                if children:
                    self._where_am_i(children, current_guess)
    
    def _process_callbacks(self):
        """ Call all the callbacks """
        for cb_function, cb_items in self.callbacks.iteritems():
            cb_function(self, **cb_items)
        
    def _reduce_under_permissions(self, menu_list):
        """ Recurse menu_list and remove items that fail 
            indicated permissions testing
        """
        # We iterate in reverse as we are removing items
        for element_number in range(len(menu_list)-1, -1, -1):
            element = menu_list[element_number]
            if ('permission' in element and
                'permission_tester' in element):
                if not element['permission_tester'](element['permission'],
                                                    self.request,
                                                    ):
                    del menu_list[element_number]
                    continue
            self._reduce_under_permissions(element.get('children', []))

    def _remove_dangling_elements(self, menu_list):
        """ Remove any elements that do not resolve to a link """
        # We iterate in reverse as we are removing items
        for element_number in range(len(menu_list)-1, -1, -1):
            element = menu_list[element_number]
            # Depth first.
            self._remove_dangling_elements(element.get('children', []))
            if (not element.get('children', []) and
                not element.get('link', None)):
                del menu_list[element_number]

    def _identify_parents(self, menu_list, parent_set=None, back_link=None):
        """ Build a reverse link in each element to it's parent.

            The last item is always the element itself.
            
            :parent_set: is a list of node titles

            :back_list: is s list of node references
        """
        if not parent_set:
            parent_set = []
            back_link = []
        for element in menu_list:
            element['parent'] = parent_set
            element['back_link'] = back_link
            self._identify_parents(
                element.get('children', []),
                parent_set[:].append(element.get('title', 'unknown')),
                back_link[:].append(element))

    def _sort_menu(self, menu_list):
        """ Sort each level of the menu according to position """
        for element in menu_list:
            if 'children' in element:
                self._sort_menu(element['children'])
        # Sort using key position
        menu_list.sort(key=lambda x:x.get('position', 999))

    def element_is_open(self, element):
        """ An element is open (can be rendered) if it is:

            - not posessed of a link - there must be at least one link
              further down, otherwise it would have been trimmed

            - under a parent that does not have a link  
            
            - at the top level (zero len parents)

            - on the path to the current page

            - a child of the current page

            - a sibling of current page and current has no children
        """
        if not 'link' in element:
            return True

        back_link = element.get('back_link', [])
        if len(back_link) > 1 and not 'link' in back_link[-2]:
            return True
        if len(back_link) <= 1:
            # Top level
            return True

        parent_set = element.get('parent', [])
        current_page = []
        if self.current and len(self.current) > 2:
            current_page = self.current[2]
        if len(parent_set) <= len(current_page):
            if parent_set == current_page[:len(parent_set)]:
                # Child or on path of current
                return True
        return False

    
#-----------------------------------------------------------------------
