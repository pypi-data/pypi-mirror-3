#####################################################################
# vs.contentpopup
# (C) 2011, Veit Schiele Communications GmbH
#####################################################################

from transformation import Transformer

def postEdit(event):
   
    obj = event.object

    field = obj.Schema().getField('text')
    if not field:
        return

    # only modify text/html text fields (omit fields with reST etc.)
    if field.getContentType(obj) in ('text/html',):
        T = Transformer(['addUUIDs'])
        html = T(obj.getText(), input_encoding='utf-8')
        obj.setText(html)
        obj.setContentType('text/html')
        obj.getField('text').setContentType(obj, 'text/html')
