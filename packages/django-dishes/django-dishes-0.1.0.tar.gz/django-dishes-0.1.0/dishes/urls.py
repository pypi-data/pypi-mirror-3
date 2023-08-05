from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView, edit
from dishes.models import Dish, Menu


# custom views vendors
urlpatterns = patterns('',
    url(r'^menus/$', view=ListView.as_view(model=Menu, queryset=Menu.active_objects.all()), name="ds-menu-list"),
    url(r'^menus/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=Menu), name="ds-menu-detail"),
    url(r'^menus/add/$', view=edit.CreateView.as_view(model=Menu), name="ds-menu-add"),
    url(r'^menus/(?P<slug>[-\w]+)/edit/$', view=edit.UpdateView.as_view(model=Menu), name="ds-menu-edit"),
    url(r'^menus/(?P<slug>[-\w]+)/delete/$', view=edit.DeleteView.as_view(model=Menu), name="ds-menu-delete"),

	#url(r'^animals/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=Genus), name="fm-genus-detail"),
)
