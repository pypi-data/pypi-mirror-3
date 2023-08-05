"""Definition of the Boardfile content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import file
 
from medialog.boardfile import boardfileMessageFactory as _
from medialog.boardfile.interfaces import IBoardfile
from medialog.boardfile.config import PROJECTNAME

 
BoardfileSchema = file.ATFileSchema.copy() + atapi.Schema((
    # -*- Your Archetypes field definitions here ... -*-


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

BoardfileSchema['title'].storage = atapi.AnnotationStorage()
BoardfileSchema['title'].widget.label = 'Journal - Conference - Report - Thesis'
BoardfileSchema['title'].required = True
BoardfileSchema['description'].storage = atapi.AnnotationStorage()
BoardfileSchema['description'].widget.label = 'Abstract'
BoardfileSchema['description'].required = False
BoardfileSchema['file'].widget.label = 'doc, .pdf or .zip file to upload'
BoardfileSchema['file'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(BoardfileSchema, moveDiscussion=False)

class Boardfile(file.ATFile):
    """Boardfile content type"""
    implements(IBoardfile)

    meta_type = "boardfile"
    schema = BoardfileSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    file = atapi.ATFieldProperty('file')

    wp = atapi.ATFieldProperty('wp')

    
atapi.registerType(Boardfile, PROJECTNAME)
