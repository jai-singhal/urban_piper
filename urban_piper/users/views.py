from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from .forms import UsersLoginForm
# from .backend import AuthenticationBackend


def login_view(request):
	form = UsersLoginForm(request.POST or None)
	if form.is_valid():
		username = form.cleaned_data.get("username")
		password = form.cleaned_data.get("password")
		user = authenticate(username = username, password = password)
		print(user)
		login(request, user)
		
		if user.is_storage_manager:
			messages.success(request, "Successfully login as Storage Manager")
			return redirect(reverse("core:storage_manager"))
		elif user.is_delivery_person:
			messages.success(request, "Successfully login as Delivery Person")
			return redirect(reverse("core:delivery_person"))
		else:
			return HttpResponse("<h1>You are neither storage person or delivery person. Try again later</h1>")

		
	return render(request, "login.html", {
		"form" : form,
		"title" : "Login",
	})

def logout_view(request):
	logout(request)
	return HttpResponseRedirect("/")