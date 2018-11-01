from django.core.management import BaseCommand

from news.scrapers.newsapi_org import NewsApiOrgScraper


class Command(BaseCommand):
    help = f'Download news from apinews.org'

    def add_arguments(self, parser):
        parser.add_argument(
            '-k', '--apikey',
            dest='apikey', type=str, required=True,
            help=f'Apikey for apinews.org site'
        )

        parser.add_argument(
            '-c', '--count',
            dest='count', type=int, default=100,
            help='Limit for downloading news',
        )

        parser.add_argument(
            '-t', '--theme',
            dest='theme', type=str, default=f'everything',
            help='End point path for downloading news'
        )

        parser.add_argument(
            '-q',
            dest='q', type=str, default=f'python',
            help='q parameter for requests'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(f'Starting task for downloading {options["count"]} news from apinews.org'))

        scrapper = NewsApiOrgScraper(api_key=options['apikey'])
        downloaded_news = scrapper.start(options['count'], params={'q': options['q']}, path=options['theme'])

        self.stdout.write(self.style.SUCCESS(f'Task completed, downloaded {downloaded_news} news'))
