from django.forms import ModelForm
from .models import DeliveryTask


class DeliveryTaskForm(ModelForm):
    class Meta:
        model = DeliveryTask
        exclude = ("created_by", "creation_at", "assigned_to", "state")

    def __init__(self, *args, **kwargs):
        super(DeliveryTaskForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                "name":"username"})
