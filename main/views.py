from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import random
import json
from django.contrib.auth import authenticate, login, logout
from models import Profile
from PiLockUnlockScripts.unlock import unlock
import os, sys
from PiLock.settings import getApiVersion, getRoot, BASE_DIR
from django.utils.crypto import get_random_string
import yaml

# Create your views here.

def ReadConfig():
    fin = open(BASE_DIR+"/config.yml", "r")
    conf = yaml.load(fin)
    fin.close()
    return conf

# I might implement this later on...
# def writeNewServerID():
#     fi = open(BASE_DIR+"/server_id", "w")
#     key = get_random_string(length=64, allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)")
#     fi.write(key)
#     fi.close()
#     os.chmod("server_id", 400)
#     return key
#
# def getServerID():
#     try:
#         fin = open(BASE_DIR + "/server_id", "r")
#         ServerID = fin.read()
#         fin.close()
#     except IOError:
#         ServerID = writeNewServerID()
#     return ServerID

def get_auth_token():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)


def get_random_pin():
    chars = '1234567890'
    return get_random_string(6, chars)


@csrf_exempt
def loginView(request):
    # View for "logging" the user in.
    # Returns a JSON response with the user's auth token if the user hasn't already logged in,
    # else kicks the user out.#
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
    if request.method == "POST":  # Same as above, only accept POST requests
        if "authToken" not in request.POST or "pin" not in request.POST:  # Check if both the PIN and the AuthToken are inside the POST request.
            return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)
        else:
            givenpin = request.POST["pin"]
            givenauthtoken = request.POST["authToken"]
            if Profile.objects.filter(pin=givenpin, authToken=givenauthtoken).count() > 0:
                unlock()
                return HttpResponse(json.dumps({"message": "SUCCESS"}), status=200)
            else:
                return HttpResponse(json.dumps({"message": "UNAUTHORIZED"}), status=401)


@csrf_exempt
def changePin(request):
    if request.method == "POST":
        if "authToken" not in request.POST or "oldPin" not in request.POST or "newPin" not in request.POST:
            return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)
        else:
            token = request.POST["authToken"]
            oldpin = request.POST["oldPin"]
            newpin = request.POST["newPin"]
            #Searching for a profile with authToken and pin matching the values sent in POST request
            if Profile.objects.filter(authToken=token, pin=oldpin).count() > 0:
                tobeupdate = Profile.objects.get(authToken=token, pin=oldpin)
                tobeupdate.pin = newpin
                tobeupdate.save()
                return HttpResponse(json.dumps({"message": "SUCCESS"}), status=200)
            else:
                return HttpResponse(json.dumps({"message": "UNAUTHORIZED"}), status=401)
    else:
        return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)


def index(request):
    # return render(request, 'index.html', context)
    # Returns response with server's status (AKA: Heartbeat)
    if ReadConfig()["enabled"]:
        return HttpResponse(json.dumps({"status": "ALIVE", "version": getApiVersion()}))
    else:
        return HttpResponse(json.dumps({"status": "LOCKED", "version": getApiVersion()}))
