# coding: utf-8
import re
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import Interface
from Products.CMFCore.interfaces import ISiteRoot
# from Products.CMFCore.permissions import ChangeLocalRoles

from Products.CMFCore.utils import getToolByName
# from Products.CMFCore.utils import _checkPermission
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import re

SNIPPET_LEN = 40

def _to_str(s):
    assert isinstance(s, basestring)
    if not isinstance(s, str):
        s = s.encode('utf-8')
    return s

def _to_unicode(s):
    assert isinstance(s, basestring)
    if not isinstance(s, unicode):
        s = s.decode('utf-8')
    return s

def _is_word(s, re_word):
    s = _to_unicode(s)
    return re_word.search(s)

def _snippet_body(s, re_word):
    s = _to_unicode(s)
    index = re_word.search(s)
    if index is not None:
        idx = index.start(0)
    else:
        idx = 0
    return s[idx:idx+SNIPPET_LEN]

#def _replace_word(s, re_word, word):
#    pass


def _replace_body(obj, body, field_name, re_org_word, replaced_word):
    kwargs = {}
    format = 'text/html'
    if field_name == 'text':
        format = obj.text_format
    changed_to_unicode = False
    data = body
    if not isinstance(data, unicode):
        data = _to_unicode(data)
        changed_to_unicode = True
    is_modify_filed = False
    if format == 'text/html':
        result = re_org_word.sub(replaced_word, data)
        kwargs['mimetype'] = 'text/html'
        is_modify_filed = True
    elif format == 'text/x-rst':
        result = re_org_word.sub(replaced_word, data)
        kwargs['mimetype'] = 'text/restructured'
        is_modify_filed = True
    if not is_modify_filed:
        return field_name
    if changed_to_unicode:
        result = _to_str(result)
    kwargs['field'] = field_name
    obj.getField(field_name).set(obj, result, **kwargs)
    obj.reindexObject()


class IReplaceWordPanel(ISiteRoot):
    """Replace word content
    """

class ReplaceWordPanel(BrowserView):
    implements(IReplaceWordPanel)

    template = ViewPageTemplateFile('replace.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if self.request.form.get('form.submited') == '1':
            org_word = self.request.form.get('original-word', '').strip()
            self.re_org_word = re.compile(r'%s' % org_word, re.UNICODE)
            self.replaced_word = self.request.form.get('replace-word').strip()
#            self.result = self._replace_word(contentsinfo=None)
        return self.template()


    def get_replaced_content(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        c_type = self.request.form.get('content-type', '').strip()
        c_field = self.request.form.get('content-field', '').strip()
        dry_run = self.request.form.get('dry-run')
        confirm = self.request.form.get('replace-confirm')

        kw = {'portal_type' : c_type}
        items = catalog(**kw)
        for item in items:
            obj = item.getObject()
            title = item.Title
            url = item.getURL()
            field = obj.getField(c_field)
            if field is None:
                continue
            body = field.getRaw(obj)
            if not _is_word(body, self.re_org_word):
                continue
            if dry_run:
                result = 'no replace'
            elif confirm:
                result = 'replace'
                _replace_body(obj, body, c_field, self.re_org_word, self.replaced_word) #TODO:
            else:
                result = 'no replace'
            yield dict(result=result, title=title, url=url,
                            body=_snippet_body(body, self.re_org_word))
