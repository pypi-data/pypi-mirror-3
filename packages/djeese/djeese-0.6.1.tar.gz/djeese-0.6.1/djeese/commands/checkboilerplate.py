from __future__ import with_statement
from djeese.boilerplates import BoilerplateConfiguration
from djeese.commands import BaseCommand, CommandError
import os
import sys

class Command(BaseCommand):
    help = 'Validate a djeese boilerplate.'

    def handle(self, boilerplate=None, **options):
        if not boilerplate:
            raise CommandError("You must provide the path to your boilerplate file as first argument")
        if not os.path.exists(boilerplate):
            raise CommandError("Boilerplate file %r not found." % appfile)
        boilerplatecfg = BoilerplateConfiguration(int(options['verbosity']))
        boilerplatecfg.read(boilerplate)
        if not boilerplatecfg.validate():
            sys.exit(1)
