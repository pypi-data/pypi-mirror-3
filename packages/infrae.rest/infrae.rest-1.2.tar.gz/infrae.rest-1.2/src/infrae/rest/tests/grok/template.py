# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
"""

  Let's first grok our test first:

   >>> grok('infrae.rest.tests.grok.template')

  Now, if we have a folder we can use our REST component:

    >>> root = getRootFolder()
    >>> root.manage_addProduct['OFS'].manage_addFolder('folder', 'Folder')

  We can now fetch the component with the template:

    >>> print http('GET /folder/++rest++form HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 30
    Content-Type: text/html;charset=utf-8
    <BLANKLINE>
    <form>
       <h1>42</h1>
    </form>
    <BLANKLINE>

  And the nested one as well:

    >>> print http('GET /folder/++rest++form/widget HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 15
    Content-Type: text/html;charset=utf-8
    <BLANKLINE>
    <span>51</span>


"""

from OFS.Folder import Folder
from five import grok
from infrae.rest import RESTWithTemplate


class FormTemplate(RESTWithTemplate):
    grok.context(Folder)
    grok.name('form')


    def value(self):
        return '42'

    def GET(self):
        return self.template.render(self)


class WidgetTemplate(RESTWithTemplate):
    grok.adapts(FormTemplate, Folder)
    grok.name('widget')

    def value(self):
        return '51'

    def GET(self):
        return self.template.render(self)


# Let's use an inline template here
widgettemplate = grok.PageTemplate('<span tal:content="rest/value"></span>')
