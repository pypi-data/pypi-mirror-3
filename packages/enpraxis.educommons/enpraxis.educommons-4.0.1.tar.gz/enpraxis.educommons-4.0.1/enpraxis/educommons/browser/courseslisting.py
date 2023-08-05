from zope.publisher.browser import BrowserView


class CoursesListing(BrowserView):
    """ List of Schools """

    def getListings(self, brains):
        if brains:
            numb = len(brains)
            num = numb/2
            if numb%2:
                num += 1
            return brains[:num], brains[num:]
        else:
            return [],[]

    def schoolsEnabled(self):
        portal = self.context.portal_url.getPortalObject()
        ecprops = portal.portal_properties.educommons_properties
        return ecprops.getProperty('school_enable')

    def getSchools(self):
        """ Get list of Schools """
        portal = self.context.portal_url.getPortalObject()
        brains = portal.portal_catalog.searchResults(
            path={'query':'/'.join(portal.getPhysicalPath())+'/',},
            Type='School',
            sort_on='sortable_title')
        if brains:
            return brains
        return []

    def getDivisions(self, school=None):
        """ Get list of divisions from school """
        portal = self.context.portal_url.getPortalObject()
        if school:
            brains = portal.portal_catalog.searchResults(
                path={'query':school.getPath(),},
                Type='Division',
                sort_on='sortable_title')
        else:
            brains = portal.portal_catalog.searchResults(
                path={'query':'/',},
                Type='Division',
                sort_on='sortable_title')
            
        return brains


class DivisionListing(BrowserView):
    """ List of divisions """

    def getSections(self):
        """ Get list of Divisions """
        brains = self.context.portal_catalog.searchResults(
            path={'query':'/'.join(self.context.getPhysicalPath())+'/',},
            Type='Division')
        return brains
        
