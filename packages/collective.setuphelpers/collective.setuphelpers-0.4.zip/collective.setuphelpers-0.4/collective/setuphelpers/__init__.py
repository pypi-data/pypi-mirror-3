# The import below imports not yet initialized packages - the tests fail
#from structure import setupStructure, clearUpSite
from various import (
    setupCatalog,
    registerDisplayViews,
    unregisterDisplayViews,
    hideActions,
    registerActions,
    setupTinyMCE,
    setupCTAvailability,
    setupHTMLFiltering,
    registerTransform,
    unregisterTransform,
    setHomePage,
    setupNavigation,
    hidePortletTypes,
)

from usersandgroups import (
    createGroups,
    enableSelfRegistration
)
