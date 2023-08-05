from zope import schema
from zope.interface import Interface 

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from medialog.boardfile import boardfileMessageFactory as _


class IBoardfile(Interface):
    """Boardfile content type"""
    

    wp = schema.TextLine(
        title=_(u"WP"), 
        required=True,
        description=_(u"Select one"),
    )


    file = schema.Bytes(
        title=_(u"File"), 
        required=True,
        description=_(u"File to upload. If you have many, please zip them first"),
    )
 
