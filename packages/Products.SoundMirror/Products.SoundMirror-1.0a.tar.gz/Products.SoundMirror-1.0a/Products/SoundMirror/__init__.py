from Products.Archetypes.atapi import FileWidget, AnnotationStorage
from plone.app.blob.field import FileField

sound = FileField('sound',
          required=False,
          searchable=True,
          storage = AnnotationStorage(migrate=True),
          widget = FileWidget(
          description = '',
          #FIXME
          #label=_(u'sound', default=u'Lyd'),
          show_content_type = False,),
)

from Products.PatchPloneContent import content_classes_add_fields, content_classes

content_classes_add_fields(content_classes, (sound,))
