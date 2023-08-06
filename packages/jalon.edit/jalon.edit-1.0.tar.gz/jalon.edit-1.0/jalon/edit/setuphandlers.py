# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.lib import constraintypes

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('jalon.edit-various.txt') is None:
        return

    # Add additional setup code here

def installHandler(self):
    if self.readDataFile('jalon.edit-install.txt') is None:
        return

    portal = self.getSite()
    qi = getToolByName(portal, 'portal_quickinstaller')
    #a venir jalon.exist
    listeInstall = ["collective.quickupload", "Products.Collage", "collective.fancybox", "jalonedit.theme", "jalonedit.content"]
    for mod in listeInstall:
        if not qi.isProductInstalled(mod):
           # there is no GS profile for mod.
           qi.installProduct(mod)

def updateCatalog(self, clear=True):
    if self.readDataFile('jalon.edit-install.txt') is None:
        return

    portal = self.getSite()

    listeExcludePortal = ["news", "events", "Members"]
    for rep in listeExcludePortal:
        if hasattr(portal, rep):
           obj = getattr(portal, rep)
           obj.setTitle(rep.capitalize())
           obj.setExcludeFromNav(True)

    cours = getattr(portal, "cours")
    cours.setConstrainTypesMode(constraintypes.ENABLED)
    cours.setLocallyAllowedTypes(["Collage", "Folder"])
    cours.setImmediatelyAddableTypes(["Collage", "Folder"])


    listeExcludeCours = ["presentation", "glossaire", "webographie", "bibliographie", "fichiers", "credits", "aide", "mentions"]
    for rep in listeExcludeCours:
        if hasattr(cours, rep):
           obj = getattr(cours, rep)
           obj.setTitle(rep.capitalize())
           obj.setExcludeFromNav(True)
           if rep == "presentation": 
              obj.setLayout("presentation_view")
              obj.setConstrainTypesMode(constraintypes.ENABLED)
              obj.setLocallyAllowedTypes(["BlocPresentation"])
              obj.setImmediatelyAddableTypes(["BlocPresentation"])
           if rep in ["glossaire", "webographie", "bibliographie"]:
              obj.setConstrainTypesMode(constraintypes.ENABLED)
              obj.setLayout("ressource_view")
           if rep in ["glossaire", "bibliographie"]:
              obj.setLocallyAllowedTypes([rep.capitalize()])
              obj.setImmediatelyAddableTypes([rep.capitalize()])
           if rep == "webographie": 
              obj.setLocallyAllowedTypes(["Link"])
              obj.setImmediatelyAddableTypes(["Link"])

    logger = self.getLogger('jalon.edit updateCatalog')
    logger.info('Updating catalog (with clear=%s) so items in profiles/default/structure are indexed...' % clear )
    catalog = portal.portal_catalog
    err = catalog.refreshCatalog(clear=clear)
    if not err:
        logger.info('...done.')
    else:
        logger.warn('Could not update catalog.')