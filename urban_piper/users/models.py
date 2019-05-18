from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError

class User(AbstractUser):
    is_storage_manager = models.BooleanField('storage_manager', default=False)
    is_delivery_person = models.BooleanField('delivery_person', default=False)

    def save(self, *args, **kwargs):
        if self.id: 
            if self.is_storage_manager and self.is_delivery_person:
                raise ValidationError("User can either be Storage Manager or Delivery Person")
        super(User, self).save(*args, **kwargs)
