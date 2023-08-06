##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFDefault setup handlers.

$Id: setuphandlers.py 114559 2010-07-11 09:57:11Z hannosch $
"""

from Products.CMFDefault.exceptions import BadRequest
from OFS.DTMLMethod import addDTMLMethod


def importVarious(context):
    """ Import various settings.

    This provisional handler will be removed again as soon as full handlers
    are implemented for these steps.
    """
    logger = context.getLogger('various')

    # Only run step if a flag file is present
    if context.readDataFile('various.txt') is None:
        logger.debug('Nothing to import.')
        return

    site = context.getSite()

    try:
        site.manage_addPortalFolder('Members')
        addDTMLMethod(site.Members,
                      'index_html', 'Member list', '<dtml-return roster>')
        logger.info('Members folder imported.')
    except BadRequest:
        logger.warning('Importing Members folder failed.')

    site.acl_users.encrypt_passwords = False
    logger.info('Password encryption disabled.')
