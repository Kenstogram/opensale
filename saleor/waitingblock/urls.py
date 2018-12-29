from django.conf.urls import url

from . import views
from django.views.generic import RedirectView
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.TablesView.as_view(), name='waitingblock'),
    url(r'^(?P<slug>\d+)/$', views.TablesUpdateView.as_view(), name='status_update'),
    url(r'^success/$', views.TablesView.redirect_view, name='success'),
    ]
