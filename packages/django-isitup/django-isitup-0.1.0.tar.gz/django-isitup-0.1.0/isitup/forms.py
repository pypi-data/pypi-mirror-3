from django.forms import ModelForm

from isitup.models import Service

class ServiceForm(ModelForm):
    class Meta:
        model = Service
        exclude = ('owner','frequency','status_code','last_checked',)

