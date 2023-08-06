from django.core.management.base import BaseCommand, CommandError
from s3backup import S3Backup

class Command(BaseCommand):
    args = '<storage prefix>'
    help = 'Make a database backup and store on S3. Default prefix is "daily"'
    
    def handle(self, *args, **options):
        if len(args) > 1:
            raise CommandError('Only pass one prefix as argument')
        if not len(args):
            args = ['daily']

        s3backup = S3Backup()
        result = s3backup.backup(args[0])
        self.stdout.write(result)