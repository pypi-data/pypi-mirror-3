
import time
import taskw

sh, pbs = None, None
try:
    import sh
except ImportError:
    import pbs


KEYPHRASE = "alabama"
IDLE = 0
ACCEPTING = 1
VALIDATING = 2


def speak(phrase):
    if pbs:
        print pbs.espeak(phrase)
    else:
        print sh.espeak(phrase)


def save_to_db(phrase):
    task = dict(
        description=phrase,
        priority="H",
        project="unsorted",
    )
    print "Writing %r" % task
    tw = taskw.TaskWarrior()
    tw.task_add(**task)


class TaskwarriorPlugin(object):
    def __init__(self, app):
        self.app = app
        self.state = IDLE

    def matches_keyphrase(self, phrase):
        return KEYPHRASE in phrase

    def go_idle(self):
        speak("Idling.")
        self.state = IDLE

    def handle(self, phrase):
        if self.state == IDLE and KEYPHRASE in phrase:
            speak("Yes?")
            self.state = ACCEPTING
        elif self.state != IDLE and 'never mind' in phrase:
            speak("O. K.")
            time.sleep(0.5)
            self.go_idle()
        elif self.state == ACCEPTING:
            speak(phrase)
            time.sleep(0.5)
            speak("Is that correct?")
            self.state = VALIDATING
        elif self.state == VALIDATING:
            if phrase == "yes":
                speak("Adding to DB")
                #save_to_db(phrase)
                self.go_idle()
            elif phrase == "no":
                speak("My bad.")
            else:
                speak("Wat?")
