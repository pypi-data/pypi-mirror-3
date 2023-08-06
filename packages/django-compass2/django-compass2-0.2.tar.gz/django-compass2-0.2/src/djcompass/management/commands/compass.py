#encoding: utf-8
import logging
import os
import subprocess

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import CommandError, LabelCommand
from optparse import make_option
from django.conf import settings

class Command(LabelCommand):
    help = """Compile Sass stylesheets using Compass. 
    For documentation for each primary command go to http://compass-style.org/help/tutorials/command-line/
    """
    label = "primary command"

    commands = ['compile', 'validate', 'watch',]
    standalone_commands = ['version', 'stats', 'interactive', 'frameworks']
    default_command = 'compile'

    requires_model_validation = False
    option_list = LabelCommand.option_list + (
        make_option ('-t', 
                    '--trace', 
                    action='store_true', 
                    default=False, 
                    dest='trace',
                    help="Print a full Ruby stacktrace on errors."),
        )

    def __init__(self, *args, **kwargs):
        self.primary_commands = self.commands + self.standalone_commands
        self.args = "|".join(self.primary_commands)
        return super(Command, self).__init__(*args, **kwargs)

    def handle(self, *labels, **options):
        if len(labels) > 1:
            raise CommandError('There can be only one %s.' % self.label)
        elif len(labels) == 0:
            labels = [self.default_command]
        return super(Command, self).handle(*labels, **options)

    def handle_label(self, label, **kwargs):
        if not label:
            label = self.default_command

        if label not in self.primary_commands:
            import warnings
            warnings.warn("Command %s is not implemented. Using %s as default." % (label, self.default_command), RuntimeWarning)
            label = self.default_command

        # Get the only required settings.
        input_dir = getattr(settings, 'COMPASS_INPUT', False)
        output_dir = getattr(settings, 'COMPASS_OUTPUT', False)

        if not (input_dir or output_dir):
            raise ImproperlyConfigured(
                "Please specify COMPASS_INPUT and COMPASS_OUTPUT settings")
        elif not input_dir:
            raise ImproperlyConfigured("Please specify a COMPASS_INPUT setting")
        elif not output_dir:
            raise ImproperlyConfigured("Please specify a COMPASS_OUTPUT setting")

        # Optional Django settings
        style = getattr(settings, 'COMPASS_STYLE', 'compact')
        requires = getattr(settings, 'COMPASS_REQUIRES', ())
        image_dir = getattr(settings, 'COMPASS_IMAGE_DIR', None)
        script_dir = getattr(settings, 'COMPASS_SCRIPT_DIR', None)
        relative_urls = getattr(settings, 'COMPASS_RELATIVE_URLS', False)
        executable = getattr(settings, 'COMPASS_EXECUTABLE', 'compass')

        # Build the command line
        command_line = [executable]

        #primary command
        command_line.extend([label])

        if label not in self.standalone_commands:
            #path to the project
            command_line.extend([input_dir])
            # Directories
            command_line.extend(['--sass-dir', input_dir])
            command_line.extend(['--css-dir', output_dir])
            if image_dir:
                command_line.extend(['--images-dir', image_dir])
            if script_dir:
                command_line.extend(['--javascripts-dir', script_dir])

            # Extra options
            command_line.extend(['--output-style', style])
            for requirement in requires:
                command_line.extend(['--require', requirement])
            if relative_urls:
                command_line.extend(['--relative-assets'])
            
            # Runtime options
            if kwargs['trace']:
                command_line.extend(['--trace'])
            if kwargs['verbosity'] in ('0',):
                command_line.extend(['--quiet'])
            if kwargs['verbosity'] in ('2',):
                print command_line

        logging.info(subprocess.list2cmdline(command_line))
        os.execvp(executable, command_line)

