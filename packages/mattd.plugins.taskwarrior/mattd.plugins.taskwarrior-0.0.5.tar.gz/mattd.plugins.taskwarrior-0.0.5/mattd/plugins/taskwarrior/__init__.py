import os
import time
import taskw

sh, pbs = None, None
try:
    import sh
except ImportError:
    import pbs


import logging
log = logging.getLogger("mattd")


IDLE = "idle"
ACCEPTING = "accepting"
VALIDATING = "validating"


def speak(phrase):
    if pbs:
        log.debug(pbs.espeak(phrase))
    else:
        log.debug(sh.espeak(phrase))


class TaskwarriorPlugin(object):
    def __init__(self, app):
        # First, do some validation of our config file.  Got what we need?
        if not __name__ in app.config.sections():
            raise ValueError("Couldn't find [%s] in config" % __name__)

        for attr in ['keyphrase', 'taskrc']:
            if not app.config.has_option(__name__, attr):
                raise ValueError("[%s] has no %r" % (__name__, attr))

            setattr(self, attr, app.config.get(__name__, attr))

        # Furthermore, make sure the taskrc is a real file.
        self.taskrc = os.path.abspath(os.path.expanduser(self.taskrc))
        if not os.path.exists(self.taskrc):
            raise OSError("%r does not exist" % self.taskrc)

        log.info("%r using %r" % (__name__, self.taskrc))

        self.app = app
        self.state_change(IDLE)

    def save_to_db(self, phrase):
        task = dict(
            description=phrase,
            priority="H",
            project="unsorted",
        )
        log.debug("Writing %r" % task)
        tw = taskw.TaskWarrior(self.taskrc)
        tw.task_add(**task)

    def matches_keyphrase(self, phrase):
        return self.keyphrase in phrase

    def state_change(self, new_state):
        self.state = new_state
        log.info("%r state changed to %r" % (__name__, self.state))

    def go_idle(self):
        speak("Idling.")
        self.state_change(IDLE)
        self.app.active_plugin = None

    def handle(self, phrase):
        if self.state == IDLE and self.keyphrase in phrase:
            speak("Yes?")
            self.state_change(ACCEPTING)
        elif self.state != IDLE and 'never mind' in phrase:
            speak("O. K.")
            time.sleep(0.5)
            self.go_idle()
        elif self.state == ACCEPTING:
            speak(phrase)
            self.phrase_to_save = phrase
            time.sleep(0.5)
            speak("Is that correct?")
            self.state_change(VALIDATING)
        elif self.state == VALIDATING:
            if phrase == "yes":
                speak("Adding to DB")
                self.save_to_db(self.phrase_to_save)
                self.go_idle()
            elif phrase == "no":
                speak("My bad.")
            else:
                speak("Wat?")
