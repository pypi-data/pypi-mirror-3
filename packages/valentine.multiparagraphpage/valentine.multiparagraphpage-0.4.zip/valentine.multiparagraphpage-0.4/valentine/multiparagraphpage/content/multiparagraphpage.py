"""Definition of the MultiParagraphPage content type
"""

from zope.interface import implements, directlyProvides

from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import newsitem
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.configuration import zconf
from Products.validation import V_REQUIRED

from valentine.multiparagraphpage import multiparagraphpageMessageFactory as _
from valentine.multiparagraphpage.interfaces import IMultiParagraphPage
from valentine.multiparagraphpage.config import PROJECTNAME

from valentine.multiparagraphfield import MultiParagraphField, MultiParagraphWidget

MultiParagraphPageSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
   MultiParagraphField(
       name='text',
       widget=MultiParagraphWidget(
           label='Text',
           label_msgid='multiparagraph_text_label',
           description_msgid='multiparagraph_text_description',
           i18n_domain='valentine.multiparagraphpage',
       ),
       searchable=True,
       default_output_type = 'text/x-html-safe',
   ),
   atapi.ImageField('image',
        required = False,
        storage = atapi.AnnotationStorage(migrate=True),
        languageIndependent = False,
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
        widget = atapi.ImageWidget(
            description = _(u'help_mpp_image', default=u'Will be shown in listings with thumbnails, and in the portlet for related items.'),
            label= _(u'label_news_image', default=u'Image'),
            show_content_type = False)
        ),
    atapi.StringField('imageCaption',
        required = False,
        searchable = True,
        widget = atapi.StringWidget(
            description = '',
            label = _(u'label_image_caption', default=u'Image Caption'),
            size = 40)
        ),
))

MultiParagraphPageSchema.addField(schemata.relatedItemsField.copy())


# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

MultiParagraphPageSchema['title'].storage = atapi.AnnotationStorage()
MultiParagraphPageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    MultiParagraphPageSchema,
    folderish=False,
    moveDiscussion=False
)

class MultiParagraphPage(folder.ATFolder):
    """Page with a list of manageable paragraphs"""
    implements(IMultiParagraphPage, INonStructuralFolder)

    meta_type = "MultiParagraphPage"
    schema = MultiParagraphPageSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    
    def getContentType(self,fieldname=None):
        return 'text/x-html-safe'

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return folder.ATFolder.__bobo_traverse__(self, REQUEST, name)
    

    def getParagraphsFromSlots(self):
        """
        Separate function to get paragraphs in order defined in slots (for widget editing)
        """
        paragraphs = self.getText()
        view = self.restrictedTraverse('@@multiparagraphpage_view')
        return view.getSlotParagraphs()
            

atapi.registerType(MultiParagraphPage, PROJECTNAME)
