from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.content.link import ATLink

from raptus.multilanguagefields import widgets
import fields

from base import DefaultExtender

class LinkExtender(DefaultExtender):
    adapts(ATLink)

    fields = DefaultExtender.fields + [
        fields.StringField('remoteUrl',
            required=True,
            searchable=True,
            primary=True,
            default = "http://",
            # either mailto, absolute url or relative url
            validators = (),
            widget = widgets.StringWidget(
                description = '',
                label = _(u'label_url', default=u'URL')
            )
        ),
    ]