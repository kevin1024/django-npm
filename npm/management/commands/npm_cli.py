import argparse

from django.core.management.base import BaseCommand

from npm.finders import npm_install


class Command(BaseCommand):
    help = 'Run npm install'

    def add_arguments(self, parser):
        parser.add_argument('npm_command_args', nargs=argparse.REMAINDER)

    def handle(self, *args, **options):
        npm_install(npm_command_args=options.get('npm_command_args', ()))
