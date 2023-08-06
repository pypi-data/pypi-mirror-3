Link Collection Viewlet
=======================

This package provides a little viewlet which displays links to other documents. 
If you click the links, the body of the referenced document is loaded into the 
current page using kss. By default the viewlet is placed between description 
and body text of a document. It shows only if the current context does 
reference some other documents. 

    >>> self.loginAsPortalOwner()
    >>> doc = self.portal.invokeFactory('Document', 'maindoc')
    >>> maindoc = self.portal.maindoc
    

While logged in with Modify portal contents permissions, you will see a small 
edit icon where you can manage the references. They will be stored using 
annotations on the current context.

    >>> from slc.linkcollection.interfaces import ILinkList
    >>> ILinkList(maindoc).urls
    []

tbc
