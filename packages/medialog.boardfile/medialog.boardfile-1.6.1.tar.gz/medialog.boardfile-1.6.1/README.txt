.. contents::

.. Medialog Boardfile
   -----
    
- Content type for uploading of documents that needs to be approved by many persons.
- The workflow is called "Multiapprove workflow"
- After installing you can set the group that can approve in /portal_workflow (default to "Reviewers")
- Reviewer is also added to portal_catalog index, so it is possible to make a smart folder showing only objects the current user has not approved
- Content that nobody has looked at for a certain time automatically gets published if nobody has "rejected" it.
- You will have to add clockserver after [instance] in your buildout, something like: 

zope-conf-additional =

<clock-server>
    method /mysite/@@tick
    period 120
    host localhost
    user admin
    password mypassword

</clock-server>

Please note, this product is still in the making



Espen Moe-Nilssen <espen at medialog dot no>, author