# This is necessary in Python 2.5 to enable the with statement, in 2.6
# and up it is no longer necessary.
from __future__ import with_statement
from contextlib import contextmanager

import sys
import os
import gzip
import zipfile
from optparse import make_option
import traceback

from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import (connections, router, transaction, DEFAULT_DB_ALIAS,
      IntegrityError, DatabaseError)
from django.db.models import get_apps
from django.utils.itercompat import product

try:
    import bz2
    has_bz2 = True
except ImportError:
    has_bz2 = False

class Command(BaseCommand):
    help = 'Installs the named fixture(s) in the database.'
    args = "fixture [fixture ...]"

    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a specific database to load '
                'fixtures into. Defaults to the "default" database.'),

    )

    def handle(self, *files, **options):
        using = options.get('database')
        connection = connections[using]
        self.style = no_style()

