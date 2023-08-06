from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.models import User

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from isitup.models import Service
from isitup.forms import ServiceForm

class LoginRequiredMixin(object): 
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class ServiceMixin(LoginRequiredMixin):
    model = Service
    form_class=ServiceForm

    def get_success_url(self):
        return reverse('service-list')

    def get_queryset(self):
        return Service.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)

class ServiceListView(ServiceMixin, ListView):
    pass

class ServiceDetailView(ServiceMixin, DetailView):
    pass

class ServiceCreateView(ServiceMixin, CreateView):
    pass
        
class ServiceUpdateView(ServiceMixin, UpdateView):
    pass

class ServiceDeleteView(ServiceMixin, DeleteView):
    pass
