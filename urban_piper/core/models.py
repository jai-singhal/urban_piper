from django.db import models
from django.utils.translation import gettext as _
from django.core.serializers.json import DjangoJSONEncoder
from urban_piper.users.models import User
import json

class DeliveryTaskState(models.Model):
    state_choices = (
        ("new", "New"),
        ("accepted", "Accepted"),
        ("completed", "Completed"),
        ("declined", "Declined"),
        ("cancelled", "Cancelled"),
    )
    state = models.CharField(choices = state_choices, default = "new", max_length = 12)

    def __str__(self):
        return "%s" %(self.state)

    class Meta:
        verbose_name = _("DeliveryTaskState")
        verbose_name_plural = _("DeliveryTaskStates")


class DeliveryTaskManager(models.Manager):
    def get_object_in_json(self, task_id):
        task = self.get(id = task_id)
        return json.loads(json.dumps({
            "id": task.id,
            "title": task.title,
            "priority": task.priority,
            "creation_at": task.creation_at,
            "created_by": task.created_by.username
        }, cls=DjangoJSONEncoder))


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

    objects = DeliveryTaskManager()

    class Meta:
        verbose_name = _("DeliveryTask")
        verbose_name_plural = _("DeliveryTasks")

    def __str__(self):
        return self.title

    # def get_absolute_url(self):
    #     return reverse("DeliveryTask_detail", kwargs={"pk": self.pk})


class DeliveryStateTransitionManager(models.Manager):
    def get_states_in_json(self, task_id):
        data = {
            "state" : []
        }
        for transition in self.filter(task_id = task_id).order_by("at"):
            title = transition.task.title
            data["state"].append(json.loads(json.dumps({
                "at": transition.at,
                "state": transition.state.state,
                "by": transition.by.username if transition.by else None,
            }, cls=DjangoJSONEncoder)))
        data["title"] = title

        return data


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
        unique_together = (("task", "state", "by", "at"),)

    objects = DeliveryStateTransitionManager()