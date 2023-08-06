#####################################################################
# vs.contentpopup
# (C) 2011, Veit Schiele Communications GmbH
#####################################################################

import re
from Products.Five.browser import BrowserView
from Products.CMFCore.interfaces import ISiteRoot
from Products.ATContentTypes.interfaces import IATFolder
import lxml.html

def extract_table(html, id):
    if not isinstance(html, unicode):
        html = unicode(html, 'utf-8')
    root = lxml.html.fromstring(html)
    nodes = root.xpath('//table[@id="%s"]' % id)
    if len(nodes) == 1:
        return lxml.html.tostring(nodes[0], encoding=unicode)
    return ''

class TableHandler(BrowserView):
    """ Table folding - return a rendered HTML table by its ID """

    def show_table(self, id):
        """ Return the HTML code of a table given by its id """

        if IATFolder.providedBy(self.context) or ISiteRoot.providedBy(self.context):
            default_page = self.context.getDefaultPage()
            context = self.context[default_page]
            text_field = context.getField('text')
        else:
            text_field = self.context.getField('text')
            context = self.context

        if text_field:
            self.request.response.setHeader('content-type', 'text/html;charset=utf-8')
            return extract_table(text_field.get(context), id)
