from django.conf.urls import url

from . import views
from django.views.generic import RedirectView
from django.urls import path

urlpatterns = [
    path('', views.TablesView.as_view(), name='waitingblock'),
    path('table/<int:id>/', views.TablesUpdateView.as_view(), name='status_update'),
    path('success/', views.TablesView.redirect_view, name='success'),
    ]
