from p4a.plonevideoembed import interfaces
from p4a.plonevideoembed import content
from p4a.common import site
from p4a.z2utils import utils

from Products.CMFCore import utils as cmfutils

import logging
logger = logging.getLogger('p4a.plonevideoembed.sitesetup')

try:
    import five.localsitemanager
    HAS_FLSM = True
    logger.info('Using five.localsitemanager')
except ImportError, err:
    HAS_FLSM = False

def setup_portal(portal):
    site.ensure_site(portal)
    setup_site(portal)
    setup_smart_folder_indexes(portal)

    qi = cmfutils.getToolByName(portal, 'portal_quickinstaller')
    qi.installProducts(['CMFonFive'])

INDEX_MAPPING = {'object_provides':
                    {'name': 'Interfaces provided',
                     'description': 'All interfaces provided by the given '
                                    'object.',
                     'enabled': True,
                     'criteria': ('ATSimpleStringCriterion',
                                  'ATListCriterion',)},
                 }

def setup_smart_folder_indexes(portal):
    """Adds the default indexes to be available from smartfolders"""

    atct_config = cmfutils.getToolByName(portal, 'portal_atct')

    for index, index_info in INDEX_MAPPING.items():
        atct_config.updateIndex(index, friendlyName=index_info['name'],
                                description=index_info['description'],
                                enabled=index_info['enabled'],
                                criteria=index_info['criteria'])
        atct_config.updateMetadata(index, friendlyName=index_info['name'],
                                   description=index_info['description'],
                                   enabled=True)

def setup_site(site):
    """Install all necessary components and configuration into the
    given site.

      >>> from p4a.plonevideoembed import interfaces
      >>> from p4a.common.testing import MockSite

      >>> site = MockSite()
      >>> site.queryUtility(interfaces.IVideoLinkSupport) is None
      True

      >>> setup_site(site)
      >>> site.getUtility(interfaces.IVideoLinkSupport)
      <VideoLinkSupport ...>

    """

    sm = site.getSiteManager()
    if not sm.queryUtility(interfaces.IVideoLinkSupport):
        if HAS_FLSM:
            sm.registerUtility(content.VideoLinkSupport('video_support'),
                               interfaces.IVideoLinkSupport)
        else:
            sm.registerUtility(interfaces.IVideoLinkSupport,
                               content.VideoLinkSupport('video_support'))

def _cleanup_utilities(site):
    raise NotImplementedError('Current ISiteManager support does not '
                              'include ability to clean up')

def unsetup_portal(portal):
    count = utils.remove_marker_ifaces(portal, interfaces.IVideoLinkEnhanced)
    logger.warn('Removed IVideoLinkEnhanced interface from %i objects for '
              'cleanup' % count)
