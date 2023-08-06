import os
import time

sh, pbs = None, None
try:
    import sh
except ImportError:
    import pbs

import logging
log = logging.getLogger("mattd")


class MPlayerPlugin(object):
    def __init__(self, app):
        # First, do some validation of our config file.  Got what we need?
        if not __name__ in app.config.sections():
            raise ValueError("Couldn't find [%s] in config" % __name__)

        for attr in ['keyphrase', 'target']:
            if not app.config.has_option(__name__, attr):
                raise ValueError("[%s] has no %r" % (__name__, attr))

            setattr(self, attr, app.config.get(__name__, attr))

        # Furthermore, make sure the target is a real file.
        self.target = os.path.abspath(os.path.expanduser(self.target))
        if not os.path.exists(self.target):
            raise OSError("%r does not exist" % self.target)

        self.app = app

    def matches_keyphrase(self, phrase):
        return self.keyphrase in phrase

    def go_idle(self):
        self.app.active_plugin = None

    def handle(self, phrase):
        if self.keyphrase in phrase:
            self.play()

    def play(self):
        if pbs:
            log.debug(pbs.mplayer("-quiet", self.target))
        else:
            log.debug(sh.mplayer("-quiet", self.target))
