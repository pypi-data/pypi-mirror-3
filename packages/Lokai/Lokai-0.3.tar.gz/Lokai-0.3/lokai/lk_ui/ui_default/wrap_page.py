# Name:      lokai/lk_ui/ui_default/wrap_page.py
# Purpose:   Standard view mechanism using default ident and menu
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

from werkzeug import Headers, Response, http_date
from lokai.tool_box.tb_common.exception_format import get_print_exc_plus
from lokai.tool_box.tb_common.dates import utcnow, plus_days
import lokai.lk_ui
from lokai.lk_ui.render_template import render_template

#-----------------------------------------------------------------------

def make_context(request, application_body):
    """ Returns a standard context for the default template """
    context = lokai.lk_ui.MakeIdent(request)
    context['menu_block'] = lokai.lk_ui.MakeMenu(request)
    context['application_block'] = application_body
    return context

def wrap_page(request, application_body):
    """ Returns a response object using the default template

        application_body: A block of html text that is to be placed on
        the page.

        The page is built up using the template, ident and menu
        elements that have been registered with lokai.lk_ui.
        
    """
    context = make_context(request, application_body)
    this_time = utcnow()
    old_time = plus_days(this_time, -1)
    hh = Headers()
    hh.add('Cache-Control', 'private')
    hh.add('Cache-Control', 'no-cache')
    hh.add('Cache-Control', 'no-store')
    hh.add('Cache-Control', 'must-revalidate')
    hh.add('Cache-Control', 'max-age=0')
    hh.add('Expires', http_date(old_time))
    hh.add('Last-Modified', http_date(this_time))
    hh.add('Pragma', 'no-cache')
    op = Response(render_template(lokai.lk_ui.PageTemplate, **context),
                  mimetype='text/html',
                  headers=hh
                  )
    return op

#-----------------------------------------------------------------------

EMPTY_TEMPLATE = 'lk_app_wrapper.html'

def wrap_application(request, content, template=EMPTY_TEMPLATE, **kwargs):
    """ Returns a respose object standardised for a number of
        application types.
    """
    application_page = render_template(
        template,
        page_data = content,
        **kwargs
        )
    return wrap_page(request, application_page)

#-----------------------------------------------------------------------
