#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from optparse import OptionParser
from os import remove
from os.path import join
import sys
from time import time
from traceback import format_exc

# Import from itools
import itools
from itools.core import vmsize
from itools.database import check_database, get_register_fields
from itools.fs import lfs
from itools.database import make_catalog, Resource

# Import from ikaaro
from ikaaro.server import Server, ask_confirmation
from ikaaro.server import get_fake_context



def update_catalog(parser, options, target):
    # Check the server is not started, or started in read-only mode
    server = Server(target, read_only=True, cache_size=options.cache_size)
    if server.is_running_in_rw_mode():
        print 'Cannot proceed, the server is running in read-write mode.'
        return

    # Check for database consistency
    if options.quick is False and check_database(target) is False:
        return 1

    # Ask
    message = 'Update the catalog (y/N)? '
    if ask_confirmation(message, options.confirm) is False:
        return

    # Create a temporary new catalog
    catalog_path = '%s/catalog.new' % target
    if lfs.exists(catalog_path):
        lfs.remove(catalog_path)
    catalog = make_catalog(catalog_path, get_register_fields())

    # Get the root
    root = server.root

    # Build a fake context
    context = get_fake_context(server.database)
    context.server = server

    # Update
    t0, v0 = time(), vmsize()
    doc_n = 0
    error_detected = False
    if options.test:
        log = open('%s/log/update-catalog' % target, 'w').write
    for obj in root.traverse_resources():
        if not isinstance(obj, Resource):
            continue
        if not options.quiet:
            print doc_n, obj.abspath
        doc_n += 1
        context.resource = obj

        # Index the document
        try:
            catalog.index_document(obj)
        except Exception:
            if options.test:
                error_detected = True
                log('*** Error detected ***\n')
                log('Abspath of the resource: %r\n\n' % str(obj.abspath))
                log(format_exc())
                log('\n')
            else:
                raise

        # Free Memory
        del obj
        server.database.make_room()

    if not error_detected:
        if options.test:
            # Delete the empty log file
            remove('%s/log/update-catalog' % target)

        # Update / Report
        t1, v1 = time(), vmsize()
        v = (v1 - v0)/1024
        print '[Update] Time: %.02f seconds. Memory: %s Kb' % (t1 - t0, v)

        # Commit
        print '[Commit]',
        sys.stdout.flush()
        catalog.save_changes()
        # Commit / Replace
        old_catalog_path = '%s/catalog' % target
        if lfs.exists(old_catalog_path):
            lfs.remove(old_catalog_path)
        lfs.move(catalog_path, old_catalog_path)
        # Commit / Report
        t2, v2 = time(), vmsize()
        v = (v2 - v1)/1024
        print 'Time: %.02f seconds. Memory: %s Kb' % (t2 - t1, v)
    else:
        print '[Update] Error(s) detected, the new catalog was NOT saved'
        print ('[Update] You can find more infos in %r' %
               join(target, 'log/update-catalog'))



if __name__ == '__main__':
    # The command line parser
    usage = '%prog [OPTIONS] TARGET'
    version = 'itools %s' % itools.__version__
    description = (
        'Rebuilds the catalog: first removes and creates a new empty one;'
        ' then traverses and indexes all resources in the database.')
    parser = OptionParser(usage, version=version, description=description)
    parser.add_option(
        '-y', '--yes', action='store_true', dest='confirm',
        help="start the update without asking confirmation")
    parser.add_option('--profile',
        help="print profile information to the given file")
    parser.add_option('--cache-size', default='400:600',
        help="define the size of the database cache (default 400:600)")
    parser.add_option('-q', '--quiet', action='store_true',
        help="be quiet")
    parser.add_option(
        '--quick', action="store_true", default=False,
        help="do not check the database consistency.")
    parser.add_option('-t', '--test', action='store_true', default=False,
        help="a test mode, don't stop the indexation when an error occurs")

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('incorrect number of arguments')

    target = args[0]

    # Action!
    if options.profile is not None:
        from cProfile import runctx
        runctx("update_catalog(parser, options, target)", globals(), locals(),
               options.profile)
    else:
        update_catalog(parser, options, target)
