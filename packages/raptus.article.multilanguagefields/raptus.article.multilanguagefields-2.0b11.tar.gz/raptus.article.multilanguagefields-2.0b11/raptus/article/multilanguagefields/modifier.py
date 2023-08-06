from zope.component import adapts, queryAdapter
from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaModifier
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import PloneMessageFactory as _p
from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
try: # Plone 4 and higher
    from Products.ATContentTypes.interfaces.topic import IATTopic
except: # BBB Plone 3
    from Products.ATContentTypes.interface.topic import IATTopic
from Products.validation import V_REQUIRED

from raptus.article.core.content.article import Article
from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.multilanguagefields import widgets
from raptus.multilanguagefields.patches.traverse import __bobo_traverse__
from raptus.multilanguageplone.extender import fields
from raptus.multilanguageplone.extender.base import DefaultExtender

class BaseModifier(object):
    adapts(Article)
    implements(ISchemaModifier)

    def __init__(self, context):
         self.context = context
         
    def fiddle(self, schema):
        for field in self.fields:
            lang = field._v_lang
            field.resetLanguage()
            if field.getName() in schema:
                schema.replaceField(field.getName(),field)
            field.setLanguage(lang)


class ArticleModifier(BaseModifier):
    for_package = 'raptus.article.core'

    fields = DefaultExtender.fields + [
        fields.TextField('text',
            required=False,
            searchable=True,
            validators = ('isTidyHtmlWithCleanup',),
            storage = AnnotationStorage(migrate=True),
            default_output_type = 'text/x-html-safe',
            widget = widgets.RichWidget(
                description = '',
                label = _p(u'label_body_text', default=u'Body Text'),
                rows = 25,
                allow_file_upload = zconf.ATDocument.allow_document_upload),
            schemata='default',
        ),
    ]


class TeaserModifier(BaseModifier):
    for_package = 'raptus.article.teaser'

    fields = [
        fields.ImageField('image',
            required=False,
            languageIndependent=True,
            storage = AnnotationStorage(),
            swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
            pil_quality = zconf.pil_config.quality,
            pil_resize_algo = zconf.pil_config.resize_algo,
            max_size = zconf.ATImage.max_image_dimension,
            sizes= {'large'   : (768, 768),
                    'preview' : (400, 400),
                    'mini'    : (200, 200),
                    'thumb'   : (128, 128),
                    'tile'    :  (64, 64),
                    'icon'    :  (32, 32),
                    'listing' :  (16, 16),
                   },
            validators = (('isNonEmptyFile', V_REQUIRED),
                          ('checkImageMaxSize', V_REQUIRED)),
            widget = widgets.ImageWidget(
                description = '',
                label= _p(u'label_image', default=u'Image'),
                show_content_type = False,
            )
        ),
        fields.StringField('imageCaption',
            required = False,
            searchable = True,
            widget = widgets.StringWidget(
                description = '',
                label = _p(u'label_image_caption', default=u'Image Caption'),
                size = 40
            )
        ),
    ]

try:
    import raptus.article.teaser
    __bobo_traverse__old = Article.__bobo_traverse__
    Article.__bobo_traverse__ = __bobo_traverse__
except ImportError: # no raptus.article.teaser
    pass

class AdditionalwysiwygModifier(BaseModifier):

    for_package = 'raptus.article.additionalwysiwyg'

    fields = [
        fields.TextField('additional-text',
            required=False,
            searchable=True,
            validators = ('isTidyHtmlWithCleanup',),
            storage = AnnotationStorage(migrate=True),
            default_output_type = 'text/x-html-safe',
            widget = widgets.RichWidget(
                description = '',
                label = _(u'label_additional_text', default=u'Additional Text'),
                rows = 25,
                allow_file_upload = zconf.ATDocument.allow_document_upload),
            schemata='default',
        ),
    ]

class MapsModifier(BaseModifier):
    try:
        from raptus.article.maps.content.map import Map
        adapts(Map)
    except:
        pass

    for_package = 'raptus.article.maps'

    fields = DefaultExtender.fields

    def fiddle(self, schema):
        super(MapsModifier, self).fiddle(schema)
        field = schema.get('title').copy()
        field.required = False
        schema['title'] = field

class MarkerModifier(BaseModifier):
    try:
        from raptus.article.maps.content.marker import Marker
        adapts(Marker)
    except:
        pass

    for_package = 'raptus.article.maps'

    fields = DefaultExtender.fields

class CollectionModifier(BaseModifier):
    adapts(IATTopic)
    for_package = 'raptus.article.collections'

    fields = [
        fields.StringField('more',
            required = False,
            searchable = False,
            storage = AnnotationStorage(),
            schemata = 'settings',
            widget = widgets.StringWidget(
                description = _(u'description_more', default=u'Custom text used for read more links in article components displaying this collection.'),
                label= _(u'label_more', default=u'More link'),
            )
        ),
    ]
