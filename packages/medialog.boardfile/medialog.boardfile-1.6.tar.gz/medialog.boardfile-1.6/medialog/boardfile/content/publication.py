"""Definition of the Publication content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import file
 
from medialog.boardfile import boardfileMessageFactory as _
from medialog.boardfile.interfaces import IPublication
from medialog.boardfile.config import PROJECTNAME 


from AccessControl import ClassSecurityInfo
from Products.MasterSelectWidget.MasterSelectWidget import MasterSelectWidget
from Products.MasterSelectWidget.MasterBooleanWidget import MasterBooleanWidget

from Products.validation.validators.RangeValidator import RangeValidator

from Products.validation import validation
validYear = RangeValidator("validYear", 2009, 2050)
validation.register(validYear)
 
PublicationSchema = file.ATFileSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-


    atapi.StringField(
        'publicationcategory',
        searchable = True,
		required = True,
		default = "",
		vocabulary = [('', 'Please Choose'), ('Report', 'Report'),  ('Journal', 'Journal'),  ('Conference Refereed', 'Conference refereed') , ('Conference Unrefereed', 'Conference unrefereed'), ('Thesis', 'Thesis'), ('Internal', 'Internal'), ('Oral Presentation', 'Oral Presentation'), ('Media Contact', 'Media Contact') ],
		type = """lines""",
        storage=atapi.AnnotationStorage(),
        widget=MasterSelectWidget(
            label='Publication Category',
            description='Select the Publication Category.',
            slave_fields=(
                  {'name': 'publicationtitle',
                    'action': 'show',
                    'hide_values': ('Journal', 'Conference Refereed', 'Conference Unrefereed'),
                   },
              ),
          ),
      ),
    
    atapi.StringField(
        'publicationtitle',
        visible = False, 
        default = ' ',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Journal/Conference"),
            description=_(u"Name of Journal/Conference."),
        ),
        required=True,
        searchable=True,
    ),

    atapi.LinesField(
        'authorlist',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"Authorlist"),
            description=_(u"List of publication authors"),
        ),
        required=True,
        searchable=True,
    ),

    atapi.StringField(
        'wp',
        searchable = True,
		required = True,
		default = "",
		vocabulary = [('Please Choose', 'Not set'), ('WP1', 'WP1'), ('WP2', 'WP2'), ('WP3', 'WP3'), ('WP4', 'WP4'), ('WP5', 'WP5'), ('WP6', 'WP6')],
		type = """lines""",
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            format='select',
            label=_(u"Select WP"),            
            description=_(u"The Work Package of the publication."),          
        ),
        validators=("isUnixLikeName"),
    ),
    
    atapi.FloatField(
        'deliverable',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Deliverable Number"),
            description=_(u"The Deliverable Number"),
        ),
        validators=("isInt"),
        required = False,
    ),
  
  
    atapi.IntegerField(
        'publishingyear',
        storage=atapi.AnnotationStorage(),
        vocabulary = [('Please Choose', 'Not set'), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017)],
		type = """lines""",
        widget=atapi.SelectionWidget(
            format='select',
            label=_(u"Year Published"),            
            description=_(u"Select Year."),          
        ),
        validators=("isInt", "validYear"),
        required = True,
    ),

    
))


# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PublicationSchema['title'].storage = atapi.AnnotationStorage()
PublicationSchema['title'].widget.label = 'Publication Title'
PublicationSchema['title'].widget.description='Publication Title as it appears in the Journal'
PublicationSchema['title'].required = True
PublicationSchema['description'].storage = atapi.AnnotationStorage()
PublicationSchema['description'].widget.label = 'Abstract'
PublicationSchema['description'].required = False
PublicationSchema['file'].widget.label = 'doc, .pdf or .zip file to upload'
PublicationSchema['file'].storage = atapi.AnnotationStorage()
PublicationSchema.moveField('publicationtitle', pos='top') 
PublicationSchema.moveField('publicationcategory', pos='top') 

schemata.finalizeATCTSchema(PublicationSchema, moveDiscussion=False)

class Publication(file.ATFile):
    """Publication content type"""
    implements(IPublication)

    meta_type = "Publication"
    schema = PublicationSchema

    publicationcategory = atapi.ATFieldProperty('publicationcategory')
    publicationtitle = atapi.ATFieldProperty('publicationtitle')
    
    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    authorlist = atapi.ATFieldProperty('authorlist')
    
    file = atapi.ATFieldProperty('file')

    wp = atapi.ATFieldProperty('wp')

    deliverable = atapi.ATFieldProperty('deliverable')
    
    publishingyear = atapi.ATFieldProperty('publishingyear')
    
atapi.registerType(Publication, PROJECTNAME)


