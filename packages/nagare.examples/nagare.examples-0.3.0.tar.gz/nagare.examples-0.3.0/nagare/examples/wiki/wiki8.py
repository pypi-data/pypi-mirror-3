#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Step #2 to add significative URLs : an URL of the form '.../page/<page title>'
and without a valid session id, go to the page
"""

from __future__ import with_statement

import re
import docutils.core

from nagare import component, presentation, var

from wikidata import PageData

# ---------------------------------------------------------------------------

wikiwords = re.compile(r'\b([A-Z]\w+[A-Z]+\w+)')

class Page(object):
    def __init__(self, title):
        self.title = title

    def edit(self, comp):
        content = comp.call(PageEditor(self))

        if content is not None:
            page = PageData.get_by(pagename=self.title)
            page.data = content

@presentation.render_for(Page)
def render(self, h, comp, *args):
    page = PageData.get_by(pagename=self.title)

    content = docutils.core.publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(r'<wiki>\1</wiki>', content)
    html = h.parse_htmlstring(content, fragment=True)[0]

    for node in html.getiterator():
        if node.tag == 'wiki':
            a = h.a(node.text, href='page/'+node.text).action(lambda title=unicode(node.text): comp.answer(title))
            node.replace(a)

    return (html, h.a('Edit this page', href='page/'+self.title).action(lambda: self.edit(comp)))

@presentation.render_for(Page, model='meta')
def render(self, h, comp, *args):
    return ('Viewing ', h.b(self.title), h.br, h.br,
            'You can return to the ', h.a('FrontPage', href='page/FrontPage').action(lambda: comp.answer(u'FrontPage')))

# ---------------------------------------------------------------------------

class PageEditor(object):
    def __init__(self, page):
        self.page = page

@presentation.render_for(PageEditor)
def render(self, h, comp, *args):
    content = var.Var()

    page = PageData.get_by(pagename=self.page.title)

    with h.form:
        with h.textarea(rows='10', cols='40').action(content):
            h << page.data
        h << h.br
        h << h.input(type='submit', value='Save').action(lambda: comp.answer(content()))
        h << ' '
        h << h.input(type='submit', value='Cancel').action(comp.answer)

    return h.root

@presentation.render_for(PageEditor, model='meta')
def render(self, h, *args):
    return ('Editing ', h.b(self.page.title))

# ---------------------------------------------------------------------------

class Wiki(object):
    def __init__(self):
        self.content = component.Component(None)
        self.content.on_answer(self.goto)

        self.goto(u'FrontPage')

    def goto(self, title):
        page = PageData.get_by(pagename=title)
        if page is None:
            PageData(pagename=title, data='')

        self.content.becomes(Page(title))

@presentation.render_for(Wiki)
def render(self, h, comp, *args):
    h.head.css('main_css', '''
    .document:first-letter { font-size:2em }
    .meta { float:right; width: 10em; border: 1px dashed gray;padding: 1em; margin: 1em; }
    ''')

    with h.div(class_='meta'):
        h << self.content.render(h, model='meta')
        
    h << self.content << h.hr

    h << 'View the ' << h.a('complete list of pages', href='all').action(lambda: self.goto(comp.call(self, model='all')))
    
    return h.root

@presentation.render_for(Wiki, model='all')
def render(self, h, comp, *args):
    with h.ul:
        for page in PageData.query.order_by(PageData.pagename):
            with h.li:
                h << h.a(page.pagename, href='page/'+page.pagename).action(lambda title=page.pagename: comp.answer(title))

    return h.root

# ---------------------------------------------------------------------------

# Generic method to initialize the ``Wiki`` component from the URL

# In this step, we only manage URL of the form '.../page/<page title>'
@presentation.init_for(Wiki, "(len(url) == 2) and (url[0] == 'page')")
def init(self, url, *args):
    title = url[1] # Retrieve the page title. The condition of this generic
                   # method already checks that the URL is of the form:
                   # '.../page/<page title>'
    
    # Check if a page with the wanted title exists
    page = PageData.get_by(pagename=title)
    if page is None:
        raise presentation.HTTPNotFound()

    # Go to the page
    self.goto(title)

# ---------------------------------------------------------------------------

app = Wiki
