import time

sh, pbs = None, None
try:
    import sh
except ImportError:
    import pbs


# TODO - Obviously, put these in a config file...
KEYPHRASE = ""
sound_file = "trololo.ogg"


def play(sound_file):
    if pbs:
        print pbs.mplayer("-quiet", sound_file)
    else:
        print sh.mplayer("-quiet", sound_file)


class MPlayerPlugin(object):
    def __init__(self, app):
        self.app = app

    def matches_keyphrase(self, phrase):
        return KEYPHRASE in phrase

    def go_idle(self):
        self.app.active_plugin = None

    def handle(self, phrase):
        if KEYPHRASE in phrase:
            play(sound_file)
