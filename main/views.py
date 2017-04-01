from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
from forms import LoginForm
import random
import json
from django.contrib.auth import authenticate, login, logout
from models import Profile
# Create your views here.

def get_random_string(length=12,allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(allowed_chars) for i in range(length))

def get_auth_token():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)

def get_random_pin():
    chars = '1234567890'
    return get_random_string(6,chars)

@csrf_exempt
def loginView(request):
    if request.method == "POST":
        user = authenticate(username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            user = get_object_or_404(User, username=request.POST["username"])
            authToken = get_auth_token()
            pin = get_random_pin()
            prof = Profile.objects.create(user=user, authToken=authToken, pin=pin)  # TODO Check for already existing profile.
            resp = {"auth_token": authToken, "pin":pin}
            return HttpResponse(json.dumps(resp))
        else:
            return HttpResponse(json.dumps({"message": "Invalid Credentials"}), status=403)
    else:
        return HttpResponse(json.dumps({"message": "Invalid Request"}), status=400)