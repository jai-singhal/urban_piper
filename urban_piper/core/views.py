from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
import json
from .forms import DeliveryTaskForm
from .models import DeliveryTask, DeliveryTaskState
from urban_piper.users.decorators import (
    storage_manager_req,
    delivery_person_req
)

def index(request):
    return render(request, 'index.html', {})


class StorageManagerView(View):
    template_name = "storage_manager.html"
    form_class = DeliveryTaskForm

    # @storage_manager_req
    def get_context_data(self, **kwargs):
        context = {}
        context["delivery_task_form"] = self.form_class()
        context["tasks"] = DeliveryTask.objects.all()
        return context
    
    # @storage_manager_req
    def get(self, *args, **kwargs):
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

            try:
                state_instance = DeliveryTaskState.objects.create(task_id = task_instance.id)
            except:
                return JsonResponse({
                    "success":False,
                    "errors": "Error in creating state"
                }, status=400)

            return JsonResponse({
                    "success":True,
                    "task": {
                        "title": task_instance.title,
                        "priority": task_instance.priority,
                        "creation_at": task_instance.creation_at,
                        "created_by": task_instance.created_by.username,
                    }, 
                    "state": {
                        "state": state_instance.state,
                        "created_at": state_instance.created_at
                    }
                }, status=200
            )
        return JsonResponse({"success":False}, status=400)




class DeliveryPersonView(View):
    template_name = "delivery_person.html"

    def get(self, *args, **kwargs):
        # super(DeliveryPersonView, self).get(*args, **kwargs)
        return render(self.request, self.template_name, {})


