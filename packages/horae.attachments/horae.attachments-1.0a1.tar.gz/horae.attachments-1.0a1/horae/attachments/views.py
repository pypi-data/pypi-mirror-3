import grok

from zope.publisher.interfaces import IPublishTraverse

from collective.namedfile.browser import FileView

from horae.attachments import interfaces


class Download(FileView):
    """ A view to download an attachment
    """
    grok.implements(IPublishTraverse)
    form_field = interfaces.IAttachment['file']

    def __init__(self, context, request):
        super(Download, self).__init__(context, request)
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        self.traverse_subpath.append(name)
        return self
