#tables
import django_tables2 as tables
#import datetime
#from django.utils import timezone
#from django.utils.timezone import utc
from django_tables2.utils import A
from .models import Table


class CustomerTable(tables.Table):
    name = tables.Column()
    wait = tables.Column()
    partysize = tables.Column()
    arrival_time = tables.Column()
    status = tables.Column()
    contact = tables.Column()
    seat = tables.TemplateColumn('<a href="{{status_update.url}}">✔️</a>')
#    seat = tables.TemplateColumn('<a href='{% url "status_update" table.table_pk %}'>✔️</a>',)

    class Meta:
        data = Table.objects.all()
    #    model = models.CustomerTable


class CustomerUpdateTable(tables.Table):
    name = tables.Column()
    wait = tables.Column()
    partysize = tables.Column()
    arrival_time = tables.Column()
    status = tables.Column()
    contact = tables.Column()
    seat = tables.TemplateColumn('<a href="{{status_update.url}}">✔️</a>')
    
    class Meta:
        #        data = Customer.objects.get(pk=self.kwargs.get('pk'))
        data = Table.objects.all()


#class CustomerTable(tables.Table):
#    name = tables.LinkColumn('customer-detail', args=[A,('pk')])
#    wait = tables.LinkColumn('customer-detail', args=[A,('pk')])
#    partysize = tables.LinkColumn('customer-detail', args=[A,('pk')])
#    status = tables.LinkColumn('customer-detail', args=[A,('pk')])
#
#    class Meta:
#        model = Customer
#        fields = ('name', 'partysize', 'contact', 'arrival_time')
#        attrs = {"class": "table-striped table-bordered"}
#        empty_text = "No matching customers"
