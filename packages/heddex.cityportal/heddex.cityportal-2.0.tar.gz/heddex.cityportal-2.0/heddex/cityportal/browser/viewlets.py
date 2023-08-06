from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import common


class SearchBoxViewlet(common.SearchBoxViewlet):
    """A custom version of the searchbox class
    """
    render = ViewPageTemplateFile('searchbox.pt')


class GlobalSectionsViewlet(common.GlobalSectionsViewlet):
    """A custom version of the sections class
    """
    render = ViewPageTemplateFile('sections.pt')


class GlobalFooterSectionsViewlet(common.GlobalSectionsViewlet):
    """A custom version of the sections class used in portal footer
    """
    render = ViewPageTemplateFile('sections-footer.pt')
