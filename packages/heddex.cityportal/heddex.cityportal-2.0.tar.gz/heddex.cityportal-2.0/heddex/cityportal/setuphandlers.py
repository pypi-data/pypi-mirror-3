from zope.component import getUtility
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager

from heddex.cityportal.portlets import personaltools


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('heddex.cityportal_various.txt') is None:
        return

    # Add additional setup code here
    portal = context.getSite()
    configurePortlets(portal)

def configurePortlets(portal):

    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn',
            context=portal)

    left = getMultiAdapter((portal, leftColumn,), IPortletAssignmentMapping,
            context=portal)

    if u'personaltools' not in left:
        left[u'personaltools'] = personaltools.Assignment()
