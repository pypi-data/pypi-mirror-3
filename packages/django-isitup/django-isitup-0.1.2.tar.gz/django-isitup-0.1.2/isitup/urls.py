from django.conf import settings
from django.conf.urls.defaults import *
from isitup.views import ServiceListView, ServiceDetailView, ServiceUpdateView, ServiceDeleteView, ServiceCreateView

urlpatterns = patterns('',
    url(
        r'^$', 
        view=ServiceListView.as_view(), 
    name='service-list'),
    url(
        r'^create/$', 
        view=ServiceCreateView.as_view(), 
        name='service-create'),
    url(
        r'^(?P<slug>[-\w]+)/$', 
        view=ServiceDetailView.as_view(), 
        name='service-detail'),
    url(
        r'^(?P<slug>[-\w]+)/update/$', 
        view=ServiceUpdateView.as_view(), 
        name='service-edit'),
    url(
        r'^(?P<slug>[-\w]+)/delete/$', 
        view=ServiceDeleteView.as_view(), 
        name='service-delete'),
)
