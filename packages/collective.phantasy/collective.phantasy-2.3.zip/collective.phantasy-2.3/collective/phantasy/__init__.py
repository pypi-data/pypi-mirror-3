import config
from zope.i18nmessageid import MessageFactory
phantasyMessageFactory = MessageFactory(config.I18N_DOMAIN)

import atphantasy

def initialize(context):
    """Initializer called to use Collective Phantasy as a Zope 2 product."""

    atphantasy.initializeContents(context)

