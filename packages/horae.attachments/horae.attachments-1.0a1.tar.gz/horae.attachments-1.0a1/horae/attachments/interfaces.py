from zope import interface
from zope import schema
from megrok.form import fields

from z3c.relationfield import Relation
from z3c.relationfield.interfaces import IHasRelations

from horae.core import interfaces

from horae.attachments import _


class IAttachmentsHolder(interface.Interface):
    """ Marker interface for objects adaptable to :py:class:`IAttachments`
    """


class IAttachments(interfaces.IContainer):
    """ An object having multiple attachments
    """


class IBaseAttachment(interface.Interface):
    """ Basic attachment
    """

    file = fields.BlobFile(
        title=_(u'File'),
        required=True
    )
    """ The file associated with this attachment
    """


class IAttachment(interfaces.IIntId, IBaseAttachment):
    """ An attachment referencing the associated :py:class:`horae.properties.properties.PropertyChange`
    """

    propertychange = interface.Attribute('propertychange',
        """ The associated property change
        """
    )
    """ The :py:class:`horae.properties.properties.PropertyChange` this attachment belongs to
    """


class IRelationAttachment(IAttachment, IHasRelations):
    """ An attachment using :py:class:`zc.relation` to reference the associated :py:class:`horae.properties.properties.PropertyChange`
    """

    propertychange_rel = Relation()


class IAttachmentsForm(interface.Interface):
    """ A form to add multiple attachments
    """

    attachments = schema.List(
        title=_(u'Attachment'),
        required=False,
        value_type=schema.Object(
            schema=IBaseAttachment
        )
    )
    """ A list of :py:class:`IAttachment` to be added by the user
    """
