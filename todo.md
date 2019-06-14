tasks = DeliveryTask.objects.filter(
    created_by=2).order_by("-creation_at")

DeliveryStateTransition.objects.filter(
                                    task=task
                                    ).order_by("-at").first(),


"""
            Get all the task created by Storage manager, along with the 
            last  known state
"""

from urban_piper.core.models import (
    DeliveryTask,
    DeliveryTaskState,
    DeliveryStateTransition
)

from django.db.models import Max, Sum, F, Min, Subquery, Case, When, Value, IntegerField, Q
sub_query = DeliveryStateTransition.objects.filter(
                                    task__created_by=2
                                    ).values("task").annotate(
                                        max_at= Max("at"),
                                    ).values_list("task", "max_at")

query = DeliveryStateTransition.objects.all().annotate(x)



"""
Pending tasks for a delivery person =
    If the user's last transitition state is accepted then,
    it is called as Pending task for the user
"""

query = DeliveryStateTransition.objects.filter(
                                    by_id=3
                                ).values("task").annotate(max_at= Max("at")).annotate(
                                    x = Case(
                                        When(
                                            Q(state__state="accepted") & Q(at = F("max_at")),
                                            then = 1,
                                        ),
                                        default=0,
                                        output_field=IntegerField(),
                                    )
                                ).filter(x = True)


query = DeliveryStateTransition.objects.filter(
                                    by_id=3).values("task").annotate(max_at= Max("at")).values("max_at", "task")