from django.db import models
from django.utils.translation import gettext as _
from urban_piper.users.models import User


class DeliveryTaskState(models.Model):
    state_choices = (
        ("new", "new"),
        ("accepted", "accepted"),
        ("completed", "completed"),
        ("declined", "declined"),
        ("cancelled", "cancelled"),
    )
    state = models.CharField(choices = state_choices, default = "new", max_length = 12)

    def __str__(self):
        return "%s" %(self.state)

    class Meta:
        verbose_name = _("DeliveryTaskState")
        verbose_name_plural = _("DeliveryTaskStates")


class DeliveryTask(models.Model):
    priority_choice_fields = (
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low")
    )
    title = models.CharField(max_length=180, unique = True)
    priority = models.CharField(max_length=10, choices = priority_choice_fields, default = "low")
    creation_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, 
                    on_delete= models.CASCADE,
                    limit_choices_to={
                        "is_storage_manager": True,
                        "is_delivery_person":False,
                    },
                    related_name="created_by_sm"
                )
    states = models.ManyToManyField(DeliveryTaskState, through="DeliveryStateTransition")

    class Meta:
        verbose_name = _("DeliveryTask")
        verbose_name_plural = _("DeliveryTasks")

    def __str__(self):
        return self.title

    # def get_absolute_url(self):
    #     return reverse("DeliveryTask_detail", kwargs={"pk": self.pk})

class DeliveryStateTransition(models.Model):
    at = models.DateTimeField(auto_now_add= True)
    task = models.ForeignKey(DeliveryTask, on_delete=models.CASCADE)
    state = models.ForeignKey(DeliveryTaskState, on_delete=models.CASCADE)
    by = models.ForeignKey(User, 
                    on_delete= models.CASCADE,
                    null = True, blank = True,
                )

    def __str__(self):
        return "%s_%s" %(self.task, self.state)

    class Meta:
        verbose_name = _("DeliveryStateTransition")
        verbose_name_plural = _("DeliveryStateTransitions")
        unique_together = (("task", "state"),)
