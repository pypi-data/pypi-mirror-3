# -*- coding: utf-8 -*-
from __future__ import with_statement
import shutil
import tempfile
from djeese import errorcodes
from djeese.commands import BaseCommand, CommandError
from djeese.input_helpers import ask_boolean
from djeese.printer import Printer
from optparse import make_option
import tarfile
import traceback
import os

class Command(BaseCommand):
    help = 'Clone the static files from an website'
    option_list = BaseCommand.option_list + (
        make_option( '--noinput', action='store_true', dest='noinput', default=False,
            help='Do not ask for input. Always assume yes.'
        ),
    )

    def handle(self, website=None, outputdir='static', **options):
        if not options['noinput'] and ask_boolean("Are you sure? This will override all files in %s!" % outputdir, default=True) == 'false':
            return
        printer = Printer(int(options['verbosity']), logfile='djeese.log')
        if not website:
            raise CommandError("You must provide the name of the website from which you want to clone the static files as first argument")
        url = self.get_absolute_url('/api/v1/io/static/clone/')
        session = self.login(printer, options['noinput'])
        if not session:
            return
        data = {'name': website}
        response = session.get(url, params=data)
        if response.status_code == 200:
            stage = tempfile.mkdtemp()
            try:
                self.finish_clone(response, outputdir, stage, printer)
            finally:
                shutil.rmtree(stage, ignore_errors=True)
        elif response.status_code == 400:
            self.handle_bad_request(response, printer)
            printer.always("Clone failed: Bad request")
        elif response.status_code == 403:
            printer.error("Authentication failed")
            printer.always("Clone failed")
        elif response.status_code == 502:
            printer.error("Temporarily unavailable")
            printer.always("Clone failed")
        else:
            printer.error("Unexpected response: %s" % response.status_code)
            printer.log_only(response.content)
            printer.always("Clone failed, check djeese.log for more details")
            
    
    def handle_bad_request(self, response, printer):
        code = int(response.headers.get('X-DJEESE-ERROR-CODE', 0))
        meta = response.headers.get('X-DJEESE-ERROR-META', '')
        if code == errorcodes.INVALID_WEBSITE:
            printer.error("Website with name %r not found" % meta)
        elif code == errorcodes.NO_WEBSITE:
            printer.error("You must supply a website name")
        else:
            printer.error("Unexpected error code: %s (%s)" % (code, meta))
        printer.log_only(response.content)
    
    def finish_clone(self, response, outputdir, stage, printer):
        filename = os.path.join(stage, 'download.tar.gz')
        with open(filename, 'wb') as fobj:
            fobj.write(response.content)
        try:
            tarball = tarfile.open(filename, mode='r:gz')
        except Exception:
            printer.error("Response not a valid tar file.")
            printer.always("Clone failed")
            traceback.print_exc(printer.logfile)
            return
        tarball.extractall(outputdir)
        printer.info("Clone successful")
