from django.core.management import BaseCommand

from utils.crawl_channel_lists import crawl
from utils.general import add_arguments, get_argument_values


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        add_arguments(parser)

    def handle(self, *args, **options):
        if options['log']:
            pass
        elif options['channel']:
            crawl()
        else:
            recrawl, cname, dt, save_to_db = get_argument_values(options)
            from crawl.crawl import main as start_crawl
            start_crawl(recrawl, cname, dt, save_to_db)
