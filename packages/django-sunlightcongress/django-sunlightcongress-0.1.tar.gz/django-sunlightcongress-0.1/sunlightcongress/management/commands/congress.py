from textwrap import dedent

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from sunlightcongress.models import Committee, Legislator


class Command(BaseCommand):
    """
    Management command that namespaces a number of subcommands related to the
    django-sunlightcongress package.

    A subcommand is passed as the first argument. Its value is checked against
    the list of valid subcommands (keys in the subcommands dict property), and
    if found to be valid, a method of the same name is run. If no subcommand is
    passed, the help command is automatically run, with the remaining arguments
    and options passed as parameters.

    # Runs self.fetch()
    ./manage.py congress fetch

    # Runs self.help(), printing a list of all commands and their descriptions
    ./manage.py congress

    # Runs self.help(), printing a list of all commands and their descriptions
    ./manage.py congress help

    # Runs self.help(), printing the sanitized docstring of self.fetch()
    ./manage.py congress help fetch
    """
    args = _('<subcommand> <args>')
    help = _('Runs commands related to the congress package.')

    subcommands = {
        'help': _('Lists all commands and their descriptions'),
        'fetch': _('Downloads data from the Sunlight Congress API'),
    }

    def _write_clean(self, to, str):
        """
        Dedents string and strips whitespace before writing to file handler
        (e.g. self.stdout or self.stderror)
        """
        to.write(dedent(str).strip() + '\n')

    def handle(self, *args, **options):
        """
        Determines and validates subcommand, then runs method of that name.
        """
        args = list(args)

        options['silent'] = int(options['verbosity']) > 1

        # If no subcommand is specified, assume 'help'
        try:
            subcommand = args.pop(0)
        except IndexError:
            subcommand = 'help'

        # Ensure that specified subcommand is valid
        if subcommand not in self.subcommands:
            raise CommandError(_('No command named %s') % subcommand)

        # We must special-case 'help', as Django uses that name in the
        # BaseCommand class for the parent command's help string
        if subcommand == 'help':
            subcommand = 'help_cmd'

        # Run subcommand
        getattr(self, subcommand)(*args, **options)

    def help_cmd(self, *args, **options):
        """
        This is help's docstring
        """
        args = list(args)

        try:
            method = args.pop(0)
        except IndexError:
            self._write_clean(self.stdout, _('Available subcommands:'))
            for name, helpstring in self.subcommands.items():
                self._write_clean(self.stdout, '%s: %s' % (name, helpstring,))
        else:
            self._write_clean(self.stdout, getattr(self, method).__doc__)

    def fetch(self, *args, **options):
        """
        Usage: manage.py congress fetch

        Downloads legislator and committee data from the Sunlight Congress API.
        Intended to be used as a scheduled job.
        """
        if not options['silent']:
            self._write_clean(self.stdout, _('Fetching legislators'))
        Legislator.objects.fetch()

        if not options['silent']:
            self._write_clean(self.stdout, _('Fetching committees'))
        Committee.objects.fetch()
