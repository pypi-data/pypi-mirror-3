# Name:      lokai/lk_worker/tests/scripts/test_rest_extra.py
# Purpose:   Test some reStructuredText add-ons
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

import sys
import unittest
import logging
import StringIO

from BeautifulSoup import BeautifulSoup
from werkzeug import EnvironBuilder

from lokai.tool_box.tb_common.configuration import (set_global_config_file,
                                              clear_global_config)
from lokai.lk_ui import set_server_name
from lokai.lk_ui.publisher import build_skin
from lokai.lk_ui.session import SessionRequest

from lokai.lk_worker.ui.rest_extra import render_page, find_uri, find_file

#-----------------------------------------------------------------------

#-----------------------------------------------------------------------

def setup_module():
    clear_global_config()
    config = (
        "[all]\n"
        "not_used = xxx\n"
        "[skin]\n"
        "ignore_this = xxx\n"
        "[default]\n"
        "# Provide a default for when the url is not matched\n"
        "[lk_worker]\n"
        "application_publisher = lokai.lk_worker.ui,publisher.get_lk_worker_publisher\n"
        "application_path = /pages\n"
        "menu_publisher = lokai.lk_worker.ui.publisher\n"
        )
    set_global_config_file(StringIO.StringIO(config))
    import lokai.lk_worker.ui.main_controller

def teardown_module():
    pass

#-----------------------------------------------------------------------

TryOtherInLine = (
    "Embed a :page:`page reference <OtherPage >` in-line"
    )

TryMeInLine = (
    "Embed a :page:`page reference <#>` in-line"
    )

TryDirective = (
    ".. page:: page reference <OtherPage>\n\n"
    )

TryImage = (
    ".. page_img:: #/file/att1\n  :alt: My Image\n\n"
    )

TryFigure = (
    ".. page_fig:: #/file/fig1\n  :alt: My Figure\n\n"
    )
#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        set_server_name('dummy')
        builder = EnvironBuilder(
            )
        self.environ = builder.get_environ()
        self.environ['wsgiorg.routing_args'] = ((),{'object_id': 'MyPage'})
        self.request = SessionRequest(self.environ)

    #-------------------------------------------------------------------
    
    def tearDown(self):
        clear_global_config

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : find_uri """
        link, text = find_uri('link_word')
        self.assertEqual(link, 'link_word')
        self.assertEqual(text, None)
        link, text = find_uri('display_word <link_word>')
        self.assertEqual(link, 'link_word')
        self.assertEqual(text, 'display_word')
        link, text = find_uri('link word separate')
        self.assertEqual(link, 'link word separate')
        self.assertEqual(text, None)
        link, text = find_uri('display word separate <link word separate>')
        self.assertEqual(link, 'link word separate')
        self.assertEqual(text, 'display word separate')
        link, text = find_uri('display word adjacent< link word trimmed >')
        self.assertEqual(link, 'link word trimmed')
        self.assertEqual(text, 'display word adjacent')
        link, text = find_uri('')
        self.assertEqual(link, '')
        self.assertEqual(text, None)
        link, text = find_uri(' ')
        self.assertEqual(link, '')
        self.assertEqual(text, None)
        link, text = find_uri('<link_word_in_angles>')
        self.assertEqual(link, 'link_word_in_angles')
        self.assertEqual(text, '')
        link, text = find_uri('display_word <link_word>with stuff at the end')
        self.assertEqual(link, 'link_word')
        self.assertEqual(text, 'display_word')

    def test_t002(self):
        """ test_t002 : find_file """
        obj, fil = find_file('Spaces but no file')
        self.assertEqual(obj, 'Spaces but no file')
        self.assertEqual(fil, None)
        obj, fil = find_file('file named foo/file/foo')
        self.assertEqual(obj, 'file named foo')
        self.assertEqual(fil, 'foo')
        obj, fil = find_file('/file/named/foo/file/foo')
        self.assertEqual(obj, '/file/named/foo')
        self.assertEqual(fil, 'foo')
        obj, fil = find_file('/foo/is/file/name/file/foo')
        self.assertEqual(obj, '/foo/is/file/name')
        self.assertEqual(fil, 'foo')
        obj, fil = find_file('file name empty/file/')
        self.assertEqual(obj, 'file name empty')
        self.assertEqual(fil, '')
        obj, fil = find_file('/file/foo')
        self.assertEqual(obj, '')
        self.assertEqual(fil, 'foo')
        obj, fil = find_file('file/foo')
        self.assertEqual(obj, 'file/foo')
        self.assertEqual(fil, None)

    def test_t101(self):
        """ test_t101 : In-line role """
        res = render_page(TryOtherInLine, self.request)
        html = BeautifulSoup(res)
        tag_set = html.findAll('a')
        self.assertEqual(len(tag_set), 1)
        ref = tag_set[0]
        self.assert_(ref['href'] in ['/pages/OtherPage/default',
                                     '/pages/OtherPage/'])
        self.assertEqual(ref.string, 'page reference')
        
    def test_t102(self):
        """ test_t102 : In-line role - referencing self """
        res = render_page(TryMeInLine, self.request)
        html = BeautifulSoup(res)
        tag_set = html.findAll('a')
        self.assertEqual(len(tag_set), 1)
        ref = tag_set[0]
        self.assert_(ref['href'] in ['/pages/MyPage/default',
                                     '/pages/MyPage/'])
        self.assertEqual(ref.string, 'page reference')

    def test_t103(self):
        """ test_t103 : the directive """
        res = render_page(TryDirective, self.request)
        html = BeautifulSoup(res)
        tag_set = html.findAll('a')
        self.assertEqual(len(tag_set), 1)
        ref = tag_set[0]
        self.assert_(ref['href'] in ['/pages/OtherPage/default',
                                     '/pages/OtherPage/'])
        self.assertEqual(ref.string, 'page reference')

    def test_t104(self):
        """ test_t104 : an image from an attachment """
        res = render_page(TryImage, self.request)
        html = BeautifulSoup(res)
        tag_set = html.findAll('img')
        self.assertEqual(len(tag_set), 1)
        ref = tag_set[0]
        self.assertEqual(ref['src'], '/pages/MyPage/file/att1')
        self.assertEqual(ref['alt'], 'My Image')

    def test_t105(self):
        """ test_t105 : a figure from an attachment """
        res = render_page(TryFigure, self.request)
        html = BeautifulSoup(res)
        tag_set = html.findAll('img')
        self.assertEqual(len(tag_set), 1)
        ref = tag_set[0]
        self.assertEqual(ref['src'], '/pages/MyPage/file/fig1')
        self.assertEqual(ref['alt'], 'My Figure')
        
        
#-----------------------------------------------------------------------

if __name__ == "__main__":

    import lokai.tool_box.tb_common.helpers as tbh
    options, test_set = tbh.options_for_publish()
    tbh.logging_for_publish(options)
    setup_module() 
    try:
        tbh.publish(options, test_set, TestObject)
    finally:
        try:
            teardown_module()
        except NameError:
            pass    

#-----------------------------------------------------------------------
