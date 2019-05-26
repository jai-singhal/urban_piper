from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
from django.http import JsonResponse, Http404
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
        """
            Get all the task created by Storage manager, along with the 
            last  known state
        """
        tasks = DeliveryTask.objects.filter(
            created_by=self.request.user).order_by("-creation_at")
        context["tasks"] = []
        for task in tasks:
            context["tasks"].append({
                "current_state": DeliveryStateTransition.objects.filter(
                                    task=task
                                    ).order_by("-at").first(),
                "task": task
            })

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
        user_tasks = DeliveryTask.objects.filter(
            states__deliverystatetransition__by=self.request.user).distinct()
        context["pending_tasks"] = []
        for task in user_tasks:
            if task.states.all().order_by(
                "-deliverystatetransition__at"
            ).first().state == "accepted":
                context["pending_tasks"].append(task)

        return context

    def get(self, *args, **kwargs):
        if not self.request.user.is_delivery_person:
            raise Http404
        return render(self.request, self.template_name, self.get_context_data())
