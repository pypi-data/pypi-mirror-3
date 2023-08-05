import grok

from zope import component
from zope.interface import classImplements
from zope.app.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog

from horae.core.interfaces import ISizeFormatter
from horae.layout.interfaces import IViewExtender
from horae.properties.interfaces import IHistoryPropertiesProvider, IPropertiedDisplayWidgetsProvider
from horae.properties import views
from horae.properties import properties
from horae.ticketing.interfaces import ITicket
from horae.ticketing.ticketing import Ticket
from horae.ticketing.views import ChangeTicket

from horae.attachments import _
from horae.attachments.attachments import AttachmentsWidget
from horae.attachments import interfaces

classImplements(Ticket, interfaces.IAttachmentsHolder)


class AttachmentsTicketChangeExtender(grok.Adapter):
    """ Provides fields for adding attachments to the :py:class:`horae.ticketing.views.ChangeTicket` view
    """
    grok.context(ChangeTicket)
    grok.implements(IViewExtender)
    grok.name('horae.attachments.ticket.change')

    def pre_update(self):
        self.context.form_fields = self.context.form_fields + grok.AutoFields(interfaces.IAttachmentsForm)
        self.context.form_fields['attachments'].field.order = 140

    def pre_setUpWidgets(self, ignore_request=False):
        if self.context.form_fields.get('attachments') is not None:
            self.context.form_fields['attachments'].custom_widget = AttachmentsWidget

    def post_update(self):
        pass

    def apply(self, obj, **data):
        pass

    def validate(self, action, data):
        return ()


def _attachment_list(attachments, request):
    formatter = ISizeFormatter(request)
    items = []
    for attachment in attachments:
        field = interfaces.IAttachment['file'].bind(attachment)
        file = field.get(attachment)
        if file is not None:
            items.append(u'<a href="%s">%s</a> <span class="discreet">(%s)</span>' % (u'%s/@@download/%s' % (component.getMultiAdapter((attachment, request), name='absolute_url'), attachment.file.filename),
                                                                                      attachment.file.filename,
                                                                                      formatter.format(file.getSize())))
    if not items:
        return None
    return u'<ul class="attachments"><li>%s</li></ul>' % u'</li><li>'.join(items)


class AttachmentsWidgetProvider(grok.Adapter):
    """ Provides attachment widgets for a tickets display view
    """
    grok.context(ITicket)
    grok.implements(IPropertiedDisplayWidgetsProvider)
    grok.name('horae.attachments.ticket')

    def __init__(self, context):
        self.context = context

    def widgets(self, widgets, request):
        attachments = interfaces.IAttachments(self.context).objects()
        list = _attachment_list(attachments, request)
        attachments = properties.RichTextProperty()
        attachments.id = 'attachments'
        attachments.name = _(u'Attachments')
        if list is not None:
            widgets.append(views.PropertyDisplayWidget(attachments, list, self.context, request))
        return widgets


class ExpenseAndHoursPropertiesProvider(grok.Adapter):
    """ Provides attachments properties to be displayed in the ticket history
    """
    grok.context(ITicket)
    grok.implements(IHistoryPropertiesProvider)
    grok.name('horae.attachments.ticket.history')

    def properties(self, change, properties, request):
        catalog = component.getUtility(ICatalog)
        intids = component.getUtility(IIntIds)
        list = _attachment_list([attachment.from_object for attachment in catalog.findRelations({'to_id': intids.getId(change)}) if interfaces.IAttachment.providedBy(attachment.from_object)], request)
        if list is not None:
            properties.append({'cssClass': 'separate',
                               'name': _(u'Attachments'),
                               'value': list})
        return properties
