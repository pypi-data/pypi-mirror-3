from csv import reader
from django.core.management.base import BaseCommand, CommandError
from isitup.models import Service
from datetime import datetime
from isitup import signals as custom_signals

class Command(BaseCommand):
    args = 'None'
    help = 'Checks all active services for response codes'

    def handle(self, *args, **options):
        services = Service.objects.filter(active=True)
        for service in services:
            service.check_status_code()
            if service.ongoing_outages():
                for o in service.ongoing_outages():
                    if service.status_code == 200:
                        o.end = datetime.now()
                        o.save()
                        custom_signals.response_error_resolved.send(sender=self, 
                                                     instance=self, 
                                                     host=service.host, 
                                                     user=service.owner,
                                                     template='isitup/response_error_resolved_email.txt',
                                                     recipients=service.recipients,
                                                     response_code=service.status_code)
                    
            self.stdout.write('Service: %s - Code: %s\n' % (service.title, service.status_code))
        self.stdout.write('Successfully checked status code for %s services\n' % services.count())
