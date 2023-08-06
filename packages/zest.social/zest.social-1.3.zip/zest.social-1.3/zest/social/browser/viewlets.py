# -*- coding: utf-8 -*-
import logging
from plone.app.layout.viewlets.common import ViewletBase

from zest.social import config

logger = logging.getLogger('zest.social')


class ZestSocialAddThisViewlet(ViewletBase):

    def show(self):
        try:
            # Try to get the field using the normal accessor:
            return self.context.show_social_viewlet
        except AttributeError:
            # Either the field does not exist, or we need to call
            # getField once on this context to make it work.  Might be
            # a problem with archetypes.schemaextender (or at least
            # something I did not expect).
            try:
                value = self.context.getField(
                    'show_social_viewlet').get(self.context)
            except AttributeError:
                # Okay, the field really does not exist, fine.
                logger.debug('Using fallback show_social_viewlet=%r on %s',
                             config.SHOW_VIEWLET_FALLBACK,
                             self.context.absolute_url())
                return config.SHOW_VIEWLET_FALLBACK
            logger.debug("Got AttributeError for show_social_viewlet but "
                         "getField works! %s", self.context.absolute_url())
            return value
