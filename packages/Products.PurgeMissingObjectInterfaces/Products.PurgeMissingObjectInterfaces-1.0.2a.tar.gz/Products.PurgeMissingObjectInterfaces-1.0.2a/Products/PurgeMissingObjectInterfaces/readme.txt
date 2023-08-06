Warning: This product is highly experimental, and created without deep
knowledge/experience of the marker interfaces or ZODB machinery.  It
may start making modifications deep within the ZODB and interface
machinery as soon as it is loaded.

It's main purpose is being installed and run on an instance that has
old, broken marker interface dependencies and being used to find and
clear those dependencies.  In particular this product was built to
remove p4a (Plone 4 Artists) cruft when upgrading from Plone 3 to
Plone 4.  It should be noted that product has its own uninstallation
procedure.

To use, create an external method find, and give it the parameter
string which is a comma-separated list of package/class names to look
for and remove.  In the case of Plone 4 Artists and its dependency
dateable.chronos I used 'find?string=dateable,p4a'.

Portions copied from ZODB and zope.interface (under the ZPL).  The
rest is available under the GPL.

