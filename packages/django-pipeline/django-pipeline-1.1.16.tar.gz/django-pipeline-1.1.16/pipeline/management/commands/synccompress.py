from optparse import make_option

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--force',
            action='store_true',
            default=False,
            help='Force update of all files, even if the source files are older than the current compressed file.'
        ),
        make_option('--dry-run',
            action='store_false',
            default=True,
            help='Don\'t attempt to update files.'
        ),
        make_option('--no-cache-bust',
            dest='bust_cache',
            action='store_false',
            default=True,
            help='Don\'t update version cache.'
        )
    )
    help = 'Updates and compresses CSS and JS on-demand'
    args = '<groups>'

    def handle(self, *args, **options):
        from pipeline.packager import Packager
        packager = Packager(
            force=options.get('force', False),
            verbose=int(options.get('verbosity', 1)) >= 2
        )
        
        sync = options.get('dry_run', True)
        bust_cache = options.get('bust_cache', True)

        for package_name in packager.packages['css']:
            if args and package_name not in args:
                continue
            package = packager.package_for('css', package_name)
            if packager.verbose or packager.force:
                print
                message = "CSS Group '%s'" % package_name
                print message
                print len(message) * '-'
            packager.pack_stylesheets(package, sync=sync, bust_cache=bust_cache)

        for package_name in packager.packages['js']:
            if args and package_name not in args:
                continue
            package = packager.package_for('js', package_name)
            if packager.verbose or packager.force:
                print
                message = "JS Group '%s'" % package_name
                print message
                print len(message) * '-'
            packager.pack_javascripts(package, sync=sync, bust_cache=bust_cache)
