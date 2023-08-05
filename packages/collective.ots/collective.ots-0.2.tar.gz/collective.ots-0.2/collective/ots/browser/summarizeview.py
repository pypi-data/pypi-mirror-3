from zope.interface import implements, Interface

from Products.Five import BrowserView

from collective.ots import otsMessageFactory as _
from collective.ots.utils import summarize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ISummarizeView(Interface):
    """
    Summarize view interface
    """


class SummarizeView(BrowserView):
    """
    Summarize browser view
    """
    implements(ISummarizeView)
    template = ViewPageTemplateFile('summarizeview.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_summary(self):
        summary = ''
        if hasattr(self.context, 'Description') and hasattr(self.context, 'SearchableText'):
            text = self.context.SearchableText()
            summary = summarize(text, self.context.Language())
        return summary

    def __call__(self):
        form = self.request.form
        if form.has_key('form.button.save'):

            desc = form.get('description', '')
            self.context.setDescription(desc)
            self.request.response.redirect(self.context.absolute_url() + '/edit')
            return ''
        elif form.has_key('form.button.cancel'):
            self.request.response.redirect(self.context.absolute_url() + '/view')
            return ''
        return self.template()
