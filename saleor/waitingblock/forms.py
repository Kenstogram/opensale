from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.db import models
from django.forms import ModelForm
from .models import Table




class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = (
            'name',
            'partysize',
            'contact',
            'status',
        )
        
    def __init__(self, *args, **kwargs):
        super(TableForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
#       self.helper.form_id = 'customerform-id'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Add'))


class TableUpdateForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ('status', )
#    def update_db_field(customer, status, value):
#        Customer.objects.get(name=name).update(field=True)
#    status = models.BooleanField()

    def __init__(self, *args, **kwargs):
        super(TableUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Seat'))

#        self.helper.form_method = 'post'
#        self.helper.add_input(Submit('submit', 'Save person'))
