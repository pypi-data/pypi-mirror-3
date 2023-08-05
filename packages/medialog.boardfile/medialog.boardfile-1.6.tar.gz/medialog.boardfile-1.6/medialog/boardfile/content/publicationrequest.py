"""Definition of the Publicationrequest content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import file
 
from medialog.boardfile import boardfileMessageFactory as _
from medialog.boardfile.interfaces import IPublicationrequest
from medialog.boardfile.config import PROJECTNAME

from AccessControl import ClassSecurityInfo
from Products.MasterSelectWidget.MasterSelectWidget import MasterSelectWidget
from Products.MasterSelectWidget.MasterBooleanWidget import MasterBooleanWidget
 
PublicationrequestSchema = file.ATFileSchema.copy() + atapi.Schema((
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

    
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PublicationrequestSchema['title'].storage = atapi.AnnotationStorage()
PublicationrequestSchema['title'].widget.label = 'Publication Title'
PublicationrequestSchema['title'].widget.description='Publication Title as it appears in the Journal'
PublicationrequestSchema['title'].required = True
PublicationrequestSchema['description'].storage = atapi.AnnotationStorage()
PublicationrequestSchema['description'].widget.label = 'Abstract'
PublicationrequestSchema['description'].required = False
PublicationrequestSchema['file'].widget.label = 'doc, .pdf or .zip file to upload'
PublicationrequestSchema['file'].storage = atapi.AnnotationStorage()
PublicationrequestSchema.moveField('publicationtitle', pos='top') 
PublicationrequestSchema.moveField('publicationcategory', pos='top') 

schemata.finalizeATCTSchema(PublicationrequestSchema, moveDiscussion=False)

class Publicationrequest(file.ATFile):
    """Publicationrequest content type"""
    implements(IPublicationrequest)

    meta_type = "publicationrequest"
    schema = PublicationrequestSchema
    
    publicationcategory = atapi.ATFieldProperty('publicationcategory')
    publicationtitle = atapi.ATFieldProperty('publicationtitle')

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    file = atapi.ATFieldProperty('file')

    wp = atapi.ATFieldProperty('wp')

    
atapi.registerType(Publicationrequest, PROJECTNAME)
