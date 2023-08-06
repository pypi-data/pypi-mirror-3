import datetime as dt
import os
import subprocess
import sys

from settings import Settings

if sys.platform == 'linux2':
    import pynotify as notify
    import gtk
else:
    import Growl as notify

naf_base_path = os.path.dirname(os.path.abspath(__file__))

settings = Settings([
        os.path.join(naf_base_path, 'defaults.conf'),
        os.path.expanduser('~/.naf.conf'),
        ])

def main():
    if len(sys.argv) < 2 or (
            len(sys.argv) == 2 and (
                sys.argv[1] == u'-h'
                or sys.argv[1] == u'--help')):
        print
        print 'Usage: naf <command_to_run>'
        print
        print 'Custom configuration is read from ~/.naf.conf'
        print 'See https://github.com/knutz3n/naf for details.'
        print
        sys.exit(1)

    cr = CommandRunner(u' '.join(sys.argv[1:]))
    cr.run_command()

class CommandRunner(object):
    duration = None
    start = None
    command = None

    def __init__(self, command):
        self.command = command

    def run_command(self):
        try:
            self.start = dt.datetime.now()
            return_code = subprocess.call(self.command, shell=True)
            self.duration = dt.datetime.now() - self.start

            self.display_notification(return_code)

            sys.exit(return_code)
        except KeyboardInterrupt:
            self.handle_interrupt()
            sys.exit(2)

    def handle_interrupt(self):
        self.duration = dt.datetime.now() - self.start
        self.display_notification()

    def display_notification(self, return_code=None):
        if return_code is None and settings.aborted.show:
            description = (settings.aborted.description
                % self.string_duration())
            timeout = settings.aborted.timeout

        elif return_code == 0 and settings.success.show:
            description = (settings.success.description
                % self.string_duration())
            timeout = settings.success.timeout

        elif return_code is not None and settings.failed.show:
            description = (settings.failed.description
                % (return_code, self.string_duration()))
            timeout = settings.failed.timeout

        else:
            return

        if hasattr(notify, 'GrowlNotifier'):
            g = notify.GrowlNotifier(u'naf', notifications=['command_finished',])
            g.register()
            g.notify('command_finished', self.command, description)
        elif hasattr(notify, 'Notification'):
            if return_code == 0:
                icon = gtk.STOCK_DIALOG_INFO
            else:
                icon = gtk.STOCK_DIALOG_ERROR
            notify.init( "Notify At Finish" )
            notification = notify.Notification(self.command, description, icon)
            notification.set_timeout(timeout)
            notification.show()

    def string_duration(self):
        if self.duration.days == 0 and self.duration.seconds == 0:
            return u'0.%06d seconds'% self.duration.microseconds
        hours, remainder = divmod(self.duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        days = self.duration.days

        self.duration_string = ''
        if days > 0:
            duration_string += u'%s %s ' % (days, self.get_plural(days, u'day'))
        if hours > 0:
            self.duration_string += u'%s %s ' % (hours, self.get_plural(hours, u'hour'))
        if minutes > 0:
            self.duration_string += u'%s %s ' % (minutes, self.get_plural(minutes, u'minute'))
        if len(self.duration_string) > 0:
            self.duration_string += u'and '
        self.duration_string += u'%s %s' % (seconds, self.get_plural(seconds, u'second'))

        return self.duration_string

    def get_plural(self, value, text):
        if value == 1:
            return text
        else:
            return text + u's'

if __name__ == '__main__':
    main()
