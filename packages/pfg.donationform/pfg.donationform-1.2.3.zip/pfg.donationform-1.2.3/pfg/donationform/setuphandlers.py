from Products.CMFCore.utils import getToolByName
from pfg.donationform import HAS_PLONE40

def install_dependencies(site):
    qi = getToolByName(site, 'portal_quickinstaller')
    if not qi.isProductInstalled('getpaid.formgen'):
        qi.installProduct('getpaid.formgen')

def set_add_view_expr(context):
    # in Plone 4, the FTI needs to have the add_view_expr set.
    if HAS_PLONE40:
        ttool = getToolByName(context, 'portal_types')
        if 'Donation Form' in ttool:
            ttool['Donation Form']._updateProperty(
                'add_view_expr',
                'string:${folder_url}/+/addDonationForm'
                )

def importVarious(gscontext):
    # don't run as a step for other profiles
    if gscontext.readDataFile('is_pfgdonation_profile.txt') is None:
        return
    
    site = gscontext.getSite()
    install_dependencies(site)
    set_add_view_expr(site)
