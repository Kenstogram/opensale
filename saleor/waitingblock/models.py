import datetime
import uuid
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.timezone import utc
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User

BOOL_CHOICES = ((True, 'Waiting'), (False, 'Seated'))

class Table(models.Model):
    name = models.CharField(max_length=30)
    partysize = models.IntegerField()
    arrival_time = models.DateTimeField(auto_now_add=True, editable=False)
    contact = PhoneNumberField(blank=True)
    status = models.BooleanField(choices=BOOL_CHOICES, default=True)
    slug = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#    owner = models.ForeignKey(User, default='1', on_delete=models.CASCADE)
    highlighted = models.TextField()

    def get_time_diff(self):
        if self.arrival_time:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            timediff = now - self.arrival_time
            return timediff.total_seconds()

    wait = get_time_diff

    def save(self, *args, **kwargs):
        super(Table, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

        class Meta:
            verbose_name = 'Table'
            verbose_name_plural = 'Tables'
            ordering = ['-arrival_time']
