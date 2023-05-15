from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.views import View
from avyukt.core.forms import DeliveryTaskForm
from avyukt.core.models import (
    DeliveryTask,
    DeliveryTaskState,
    DeliveryStateTransition
)

def index(request):
    return render(request, 'index.html', {})

from django.db.models.functions import FirstValue
from django.db.models import F,  Window


class StorageManagerView(LoginRequiredMixin, View):
    template_name = "storage_manager.html"
    form_class = DeliveryTaskForm
    login_url = '/accounts/login/'
    redirect_field_name = 'sm/'

    # @storage_manager_req
    def get_context_data(self, **kwargs):
        context = {}
        context["delivery_task_form"] = self.form_class()
        """
            Get all the task created by Storage manager, along with the 
            last known state
        """

        window = {
            'order_by':  F('at').desc()
        }

        context["tasks"] = DeliveryStateTransition.objects.prefetch_related("task").filter(task__created_by = self.request.user).annotate(
            current_state= Window(FirstValue('state__state'), **window)
        )
        return context


    def get(self, *args, **kwargs):
        if not self.request.user.is_storage_manager:
            raise Http404

        return render(self.request, self.template_name, self.get_context_data())

    def post(self, *args, **kwargs):
        """
        Save the task by ajax post request
        """
        if self.request.method == "POST" and self.request.is_ajax():
            form = self.form_class(self.request.POST)
            if form.is_valid():

                title = form.cleaned_data['title']
                created_by = self.request.user
                if DeliveryTask.objects.filter(title=title, created_by=created_by).exists():
                    return JsonResponse({
                        "success": False,
                        "errors": "Title can't be duplicated"
                    }, status=400)

                task_instance = form.save(commit=False)
                task_instance.created_by = created_by
                task_instance.save()
            else:
                return JsonResponse({
                    "success": False,
                    "errors": [(k, v[0]) for k, v in form.errors.items()]
                }, status=400)

            return JsonResponse({
                "success": True,
                "task": {
                    "id": task_instance.id,
                    "title": task_instance.title,
                    "priority": task_instance.priority,
                    "creation_at": task_instance.creation_at,
                    "created_by": task_instance.created_by.username,
                }
            }, status=200
            )
        return JsonResponse({"success": False}, status=400)


class DeliveryPersonView(LoginRequiredMixin, View):
    template_name = "delivery_person.html"
    login_url = '/accounts/login/'
    redirect_field_name = 'dp/'

    def get_context_data(self, **kwargs):
        context = {}
        """
        Pending tasks for a delivery person =
            If the user's last transitition state is accepted then,
            it is called as Pending task for the user
        """
        window = {
            'order_by':  F('at').desc(),
        }

        context["tasks"] = DeliveryStateTransition.objects.prefetch_related("task").filter(by = self.request.user, state__state='accepted').annotate(
            current_state= Window(FirstValue('state__state'), **window)
        ).order_by("-at")

        return context

    def get(self, *args, **kwargs):
        if not self.request.user.is_delivery_person:
            raise Http404
        return render(self.request, self.template_name, self.get_context_data())
