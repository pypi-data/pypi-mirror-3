from plone.app.blob.field import ImageField
from Products.ATContentTypes.content import newsitem
from Products.ATContentTypes.content.newsitem import _, zconf, AnnotationStorage, ImageWidget, V_REQUIRED

newsitem.ATNewsItem.schema['image'] = \
    ImageField('image',
               required = False,
               storage = AnnotationStorage(migrate=True),
               languageIndependent = True,
               max_size = zconf.ATNewsItem.max_image_dimension,
               sizes= {'large'   : (768, 768),
                       'preview' : (400, 400),
                       'mini'    : (200, 200),
                       'thumb'   : (128, 128),
                       'tile'    :  (64, 64),
                       'icon'    :  (32, 32),
                       'listing' :  (16, 16),
                       },
               validators = (('isNonEmptyFile', V_REQUIRED),
                             ('checkNewsImageMaxSize', V_REQUIRED)),
               widget = ImageWidget(
            description = _(u'help_news_image', default=u'Will be shown in the news listing, and in the news item itself. Image will be scaled to a sensible size.'),
            label= _(u'label_news_image', default=u'Image'),
            show_content_type = False)
               )
