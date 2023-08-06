from plone.app.blob.field import ImageField
from plone.app.blob.mixins import ImageMixin
from plone.app.blob.content import ATBlob
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ModifyPortalContent

from Products.ATContentTypes.content import newsitem
from Products.ATContentTypes.content.newsitem import _, zconf, AnnotationStorage, ImageWidget, V_REQUIRED

class MyBlob:
    security = ClassSecurityInfo()

    security.declareProtected(ModifyPortalContent, 'setImage')
    def setImage(self, *arguments, **keywords):
        field = self.getField('image')
        field.set(self, *arguments, **keywords)

    security.declareProtected(ModifyPortalContent, 'getImage')
    def getImage(self, *arguments, **keywords):
        field = self.getField('image')
        return field.get(self, *arguments, **keywords)

newsitem.ATNewsItem.security = MyBlob.security
newsitem.ATNewsItem.setImage = MyBlob.setImage.im_func
newsitem.ATNewsItem.getImage = MyBlob.getImage.im_func

InitializeClass(newsitem.ATNewsItem)
    
newsitem.ATNewsItem.schema['image'] = \
    ImageField('image',
               required = False,
               mode='rw',
               mutator='setImage',
               accessor='getImage',
#               storage = AnnotationStorage(migrate=True),
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

from Products.ATContentTypes.content.schemata import finalizeATCTSchema
finalizeATCTSchema(newsitem.ATNewsItem.schema)
