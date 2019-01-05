from django.db import models
from django_tables2 import MultiTableMixin, RequestConfig
from django.views.generic import TemplateView, CreateView, UpdateView, FormView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponsePermanentRedirect

from django.contrib.auth.forms import UserCreationForm
from django.views import generic

from .models import Table
from .tables import CustomerTable, CustomerUpdateTable
from .forms import TableForm, TableUpdateForm

# Create your views here.
class TablesView(MultiTableMixin, FormView, TemplateView):
    model = Table
    template_name = 'waitingblock.html'
    context_object_name = 'Table'
    table_pagination = {'per_page': 5}
    order_by_field = ['arrival_time']
    table_class = CustomerTable
    table_data = Table.objects.all()
    #    filter_class = CustomerListFilter
    form_class = TableForm

    def get_tables(self, *args, **kwargs):
        qs = Table.objects.all()
        return [
            CustomerTable(
                qs, exclude=('arrival_time', 'contact', 'table_id','slug'))
        ]

    def form_valid(self, form):
        form.save(self.request.user)
        return super(TablesView, self).form_valid(form)

    def redirect_view(request):
        response = redirect('home')
        return response

    def get_success_url(self):
        return ('success/')

class TablesUpdateView(MultiTableMixin, FormView, TemplateView):
    model = Table
    template_name = 'waitingblock_update.html'
    context_object_name = 'status_update'
#    table_pagination = {'per_page': 1}
    order_by_field = ['arrival_time']
    table_class = CustomerUpdateTable
    table_data = Table.objects.all()
    #    filter_class = CustomerListFilter
    form_class = TableForm

    def get_tables(self, *args, **kwargs):
        qs = Table.objects.all()
        return [
            CustomerTable(
                qs, exclude=('arrival_time', 'contact', 'seat', 'slug'))
        ]

    def form_valid(self, form):
        form.save(self.request.user)
        return super(TablesView, self).form_valid(form)

    def redirect_view(request):
        response = redirect('home')
        return response

    def get_success_url(self):
        return ('success/')
