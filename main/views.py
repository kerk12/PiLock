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

def get_random_string(length=12, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(allowed_chars) for i in range(length))


def get_auth_token():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)


def get_random_pin():
    chars = '1234567890'
    return get_random_string(6, chars)


@csrf_exempt
def loginView(request):
    """ View for "logging" the user in. Returns a JSON response with the user's auth token if the user hasn't already logged in, else kicks the user out. """
    if request.method == "POST":  # Only post requests are accepted.
        if "username" not in request.POST or "password" not in request.POST:
            return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)

        user = authenticate(username=request.POST["username"],
                            password=request.POST["password"])  # Authenticate the user
        if user is not None:
            if Profile.objects.filter(user=user).count() > 0:
                # Check if the profile already exists
                return HttpResponse(json.dumps({"message": "PROFILE_REGISTERED"}))
            # Generate new random auth token and PIN
            authToken = get_auth_token()
            pin = get_random_pin()
            # Create a new profile for the user.
            prof = Profile.objects.create(user=user, authToken=authToken, pin=pin)
            resp = {"message": "CREATED", "authToken": authToken, "pin": pin}
            return HttpResponse(json.dumps(resp))
        else:
            return HttpResponse(json.dumps({"message": "INV_CRED"}), status=401)
    else:
        return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)


@csrf_exempt
def authenticateView(request):
    """ Reads the AuthToken passed in from the user, along with the pin. If they both match exactly, start the unlock script. """
    if request.method == "POST":  #Same as above, only accept POST requests
        if "authToken" not in request.POST or "pin" not in request.POST:  # Check if both the PIN and the AuthToken are inside the POST request.
            return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)
        else:
            givenpin = request.POST["pin"]
            givenauthtoken = request.POST["authToken"]
            if Profile.objects.filter(pin=givenpin, authToken=givenauthtoken).count() > 0:
                # TODO Launch the unlock script.
                return HttpResponse(json.dumps({"message": "SUCCESS"}), status=200)
            else:
                return HttpResponse(json.dumps({"message": "UNAUTHORIZED"}), status=401)
