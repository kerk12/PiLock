# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse

from .forms import LoginForm, CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import redirect
from main.models import AccessAttempt, Profile
from .models import Notification
from django.contrib.auth.decorators import login_required
import json
from django.conf import settings
from main.PiLockUnlockScripts.unlock import unlock
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.
def login_acp(request):
    if request.GET.get("logout", "0") == "1":
        logout(request)
        return render(request, "ACPLogin.html", {"logout": True})
    if request.user.is_authenticated:
        return redirect("ACP-index")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd["username"], password=cd["password"])
            # print cd
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    return redirect("ACP-index")
                return render(request, "ACPLogin.html", {"error": "The user you are trying to login as is not a staff member."}, status=403)
        return render(request, "ACPLogin.html", {"error": "Invalid username and/or password."}, status=401)
    return render(request, "ACPLogin.html")

@login_required
def index(request):
    notifications = Notification.objects.all()
    return render(request, "ACPIndex.html", {"notifications": notifications})

@login_required
def access_log_home(request):
    pages = Paginator(AccessAttempt.objects.all().order_by("-datetime"), 20, allow_empty_first_page=True)

    page = request.GET.get("p")
    access_attempts = pages.get_page(page)

    # This throws EmptyPage on render. Will need investigation.
    return render(request, "ACPAccessLog.html", {"access_attempts": access_attempts})

@login_required
def users_index(request):
    users = User.objects.all()
    return render(request, "ACPUserList.html", {"users": users})

@login_required
def create_user(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            cd = form.cleaned_data
            user.set_password(cd["password"])
            user.save()
            return redirect("ACP-Users-index")
        return render(request, "ACPUserCreate.html", {"form": form})
    return render(request, "ACPUserCreate.html", {"form": form})

@login_required
def delete_user(request, id_to_del=None):
    try:
        user = User.objects.get(id=id_to_del).delete()
    except User.DoesNotExist:
        pass
    finally:
        return redirect("ACP-Users-index")

@login_required
def delete_profile(request, user_id=None):
    try:
        profile = Profile.objects.get(user=int(user_id)).delete()
    except Profile.DoesNotExist:
        pass
    except ValueError:
        pass
    finally:
        return redirect("ACP-Users-index")

@login_required
def acp_unlock(request):
    if request.method == "POST":
        if "unlock" not in request.POST:
            return JsonResponse({"message": "INV_REQ"}, status=400)

        # TODO Might record the unlock attempt...
        if not settings.DEBUG:
            unlock()
        return JsonResponse({"message": "SUCCESS"}, status=200)
    return render(request, "ACPUnlock.html")

