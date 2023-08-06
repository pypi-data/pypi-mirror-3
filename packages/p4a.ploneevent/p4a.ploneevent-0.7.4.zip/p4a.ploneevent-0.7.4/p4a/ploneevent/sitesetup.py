from p4a.plonecalendar import content
from p4a.common import site
from p4a.z2utils import indexing
from p4a.z2utils import utils
from p4a.subtyper.sitesetup import setup_portal as subtyper_setup
from Products.CMFCore import utils as cmfutils

import logging
logger = logging.getLogger('p4a.plonecalendar.sitesetup')


def setup_portal(portal):
    site.ensure_site(portal)
    setup_profile(portal)

def setup_profile(site):
    setup_tool = site.portal_setup
    setup_tool.setImportContext('profile-p4a.ploneevent:default')
    setup_tool.runAllImportSteps()