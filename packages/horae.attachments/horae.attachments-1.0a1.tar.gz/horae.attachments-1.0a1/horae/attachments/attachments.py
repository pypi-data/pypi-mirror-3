import grok

from zope import schema
from zope import component
from zope.event import notify
from zope.app.intid.interfaces import IIntIds
from zope.formlib.widget import CustomWidgetFactory
from zope.lifecycleevent import ObjectModifiedEvent

from z3c.relationfield import RelationValue

from horae.core import container
from horae.properties.interfaces import IPropertied
from horae.layout.widgets import ObjectWidget
from horae.layout.widgets import ListSequenceWidget

from horae.attachments import interfaces


class Attachments(container.Container):
    """ An object having multiple attachments
    """
    grok.implements(interfaces.IAttachments)

    def id_key(self):
        return 'attachment'


@grok.adapter(interfaces.IAttachmentsHolder)
@grok.implementer(interfaces.IAttachments)
def attachments_of_holder(holder):
    if not 'attachments' in holder:
        holder['attachments'] = Attachments()
    return holder['attachments']


class Attachment(grok.Model):
    """ An attachment using zc.relation to reference the associated property change
    """
    grok.implements(interfaces.IRelationAttachment)

    id = schema.fieldproperty.FieldProperty(interfaces.IRelationAttachment['id'])
    file = schema.fieldproperty.FieldProperty(interfaces.IRelationAttachment['file'])
    propertychange_rel = None

    def set_propertychange(self, obj):
        intids = component.getUtility(IIntIds)
        self.propertychange_rel = RelationValue(intids.queryId(obj))
        notify(ObjectModifiedEvent(self))

    def get_propertychange(self):
        if self.propertychange_rel is None:
            return None
        return self.propertychange_rel.to_object
    propertychange = property(get_propertychange, set_propertychange)


class AttachmentsForm(grok.Adapter):
    """ An object having multiple attachments
    """
    grok.context(interfaces.IAttachmentsHolder)
    grok.implements(interfaces.IAttachmentsForm)

    def __init__(self, context):
        super(AttachmentsForm, self).__init__(context)
        self.__parent__ = self.context

    def set_attachments(self, attachments):
        propertychange = IPropertied(self.context).current()
        container = interfaces.IAttachments(self.context)
        for attachment in attachments:
            container.add_object(attachment)
            attachment.propertychange = propertychange

    def get_attachments(self):
        return []
    attachments = property(get_attachments, set_attachments)

AttachmentsWidget = CustomWidgetFactory(ListSequenceWidget, subwidget=CustomWidgetFactory(ObjectWidget, Attachment))
