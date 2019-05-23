from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
from django.http import JsonResponse, Http404
from django.db.models import Case, When, Value, IntegerField, Max, Count
from django.contrib import messages
from django.views import View
from urban_piper.core.forms import DeliveryTaskForm
from urban_piper.core.models import (
    DeliveryTask, 
    DeliveryTaskState, 
    DeliveryStateTransition
)

def index(request):
    return render(request, 'index.html', {})


class StorageManagerView(LoginRequiredMixin, View):
    template_name = "storage_manager.html"
    form_class = DeliveryTaskForm
    login_url = '/accounts/login/'
    redirect_field_name = 'sm/'

    # @storage_manager_req
    def get_context_data(self, **kwargs):
        context = {}
        context["delivery_task_form"] = self.form_class()
        tasks = DeliveryTask.objects.filter(created_by = self.request.user)
        context["tasks"] = []
        for task in tasks:
            context["tasks"].append({
                "current_state": DeliveryStateTransition.objects.filter(
                                    task = task
                                ).order_by("-at").first(),
                "task": task
            })

        return context
    
    # @storage_manager_req
    def get(self, *args, **kwargs):
        if not self.request.user.is_storage_manager:
            raise Http404 
        # super(StorageManagerView, self).get(*args, **kwargs)
        return render(self.request, self.template_name, self.get_context_data())

    # @storage_manager_req
    def post(self, *args, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            form = self.form_class(self.request.POST)
            if form.is_valid():
                task_instance = form.save(commit = False)
                task_instance.created_by = self.request.user
                task_instance.save()
            else:
                return JsonResponse({
                    "success":False,
                    "errors": [(k, v[0]) for k, v in form.errors.items()]
                }, status=400)

            return JsonResponse({
                    "success":True,
                    "task": {
                        "id": task_instance.id,
                        "title": task_instance.title,
                        "priority": task_instance.priority,
                        "creation_at": task_instance.creation_at,
                        "created_by": task_instance.created_by.username,
                    }
                }, status=200
            )
        return JsonResponse({"success":False}, status=400)




class DeliveryPersonView(LoginRequiredMixin, View):
    template_name = "delivery_person.html"
    login_url = '/accounts/login/'
    redirect_field_name = 'dp/'

    def get_context_data(self, **kwargs):
        context = {}
        user_tasks = DeliveryTask.objects.filter(
            states__deliverystatetransition__by = self.request.user).distinct()
        context["pending_tasks"] = []

        for task in user_tasks:
            if task.states.all().order_by(
                "-deliverystatetransition__at"
            ).first().state == "accepted":
                context["pending_tasks"].append(task)
                
        # context["pending_tasks"] = user_tasks.filter(
        #     state__state = "accepted", 
        # ).values("task__id", "task__title", "task__creation_at").difference(
        #     user_tasks.filter(
        #         state__state = "completed", 
        #     ).values("task__id", "task__title", "task__creation_at")
        # ).difference(
        #     user_tasks.filter(
        #         state__state = "declined", 
        #     ).values("task__id", "task__title", "task__creation_at")
        # )
        return context

    
    def get(self, *args, **kwargs):
        # super(DeliveryPersonView, self).get(*args, **kwargs)
        if not self.request.user.is_delivery_person:
            raise Http404 
        return render(self.request, self.template_name, self.get_context_data())



# DeliveryStateTransition.objects.filter(by = 2).values("task_id").annotate(
#     latest=Max('at'),
#     state
# ).annotate(
#  x = Case(
#     When(state__state = "accepted", then=1),
#     default=0,
#     output_field=IntegerField()
#     )
# ).filter(x = 1).annotate(
#     accepted= Count("task_id")
# ).values("task_id", "x", )

