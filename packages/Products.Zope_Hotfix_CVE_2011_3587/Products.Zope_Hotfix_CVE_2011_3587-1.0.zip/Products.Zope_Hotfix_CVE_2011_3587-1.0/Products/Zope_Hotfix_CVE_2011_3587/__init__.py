import logging
logger = logging.getLogger('Zope_Hotfix_CVE_2011_3587')


def initialize(context):
    from Products.Zope_Hotfix_CVE_2011_3587.patch import install_patch
    install_patch()
    logger.info('Hotfix installed.')
