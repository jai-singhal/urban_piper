from django.forms import ModelForm
from avyukt.core.models import DeliveryTask


class DeliveryTaskForm(ModelForm):
    class Meta:
        model = DeliveryTask
        exclude = ("created_by", "creation_at", "assigned_to", "states")
