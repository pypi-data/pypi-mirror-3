import logging
from types import ModuleType

logger = logging.getLogger('PloneHotfix20110928')


def initialize(context):
    from OFS.misc_ import p_

    for k, v in list(p_.__dict__.items()):
        if isinstance(v, ModuleType):
            del p_.__dict__[k]

    from Products.CMFEditions.utilities import KwAsAttributes

    if not hasattr(KwAsAttributes, '__roles__'):
        KwAsAttributes.__roles__ = ()

    logger.info('Hotfix installed.')
