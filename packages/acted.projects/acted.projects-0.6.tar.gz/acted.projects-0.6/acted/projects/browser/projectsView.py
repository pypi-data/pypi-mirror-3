from zope.interface import implements, Interface, alsoProvides

from plone.app.layout.globals.interfaces import IViewView


from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile



from zope.component import _api as zapi

from acted.projects.config import ACTED_COUNTRIES
from acted.projects.config import ACTED_SECTORS
from acted.projects.config import ACTED_DONORS
from acted.projects.config import ACTED_YEARS


class IProjectsView(Interface):
    """
    PersonsSearch view interface
    """

    def allCountries():
        """
            Method that returns all countries from the vocabulary
        """      

    def test():
        """method that does the same as test on old page templates"""

    def allDonors():
        """ get all the  donors"""

    def allSectors():
        """ get all the  sectors"""

    def allYears():
        """ get all the years """



class projectsView(BrowserView):
    """
    AddressPersons browser view
    """
    implements(IProjectsView)


    pt = ViewPageTemplateFile('templates/projectsView.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """
        This method gets called every time the template needs to be rendered
        """
        # This is needed so the actions bar will be shown.
        # the one with the actions, display, add item and workflow drop downs.
        portal_membership = getToolByName(self.context, 'portal_membership')
        if not portal_membership.isAnonymousUser():
            alsoProvides(self, IViewView)

        form = self.request.form
        path = '/'.join(self.context.getPhysicalPath())

        return self.pt()

    def allCountries(self):
        return ACTED_COUNTRIES.items()

    def allDonors(self):
        return ACTED_DONORS.items()

    def allYears(self):
        return ACTED_YEARS.items()

    def allSectors(self):
        return ACTED_SECTORS.items()

    def test(self, condition, true_value, false_value):
        """
        method that does the same as test on old page templates
        """

        if condition:
            return true_value
        else:
            return false_value


