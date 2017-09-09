from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import random
import json
from django.contrib.auth import authenticate, login, logout
from models import Profile, AccessAttempt
from PiLockUnlockScripts.unlock import unlock
import os, sys
from PiLock.settings import getServerVersion, getRoot, BASE_DIR, DEBUG
from django.utils.crypto import get_random_string
import yaml
from ipware.ip import get_ip
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

def get_watch_token():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(32, chars)


def get_random_pin():
    chars = '1234567890'
    return get_random_string(6, chars)

def parse_ip_to_model(request):
    ip = get_ip(request)
    if ip is None:
        return "0.0.0.0"
    else:
        return ip

def record_login_attempt(request, success):
    access_attempt = AccessAttempt.objects.create(usernameEntered=request.POST["username"], successful=success,
                                                  ip=parse_ip_to_model(request))

def record_unlock_attempt(request, success, profile=None):
    if profile is not None:
        access_attempt = AccessAttempt.objects.create(usernameEntered=User.objects.get(profile=profile),
                                                  successful=success, ip=parse_ip_to_model(request),
                                                  is_unlock_attempt=True)
    else:
        access_attempt = AccessAttempt.objects.create(successful=success, ip=parse_ip_to_model(request),
                                                      is_unlock_attempt=True)

@csrf_exempt
def loginView(request):
    # View for "logging" the user in.
    # Returns a JSON response with the user's auth token if the user hasn't already logged in,
    # else kicks the user out.#
    if request.method == "POST":  # Only post requests are accepted.
        if "username" not in request.POST or "password" not in request.POST:
            return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)

        if len(request.POST["username"]) > 150:
            return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)

        user = authenticate(username=request.POST["username"],
                            password=request.POST["password"])  # Authenticate the user

        if user is not None:
            record_login_attempt(request, success=True)
            if Profile.objects.filter(user=user).count() > 0:
                # Check if the profile already exists
                return HttpResponse(json.dumps({"message": "PROFILE_REGISTERED"}))
            # Generate new random auth token
            authToken = get_auth_token()

            if "passwordless" in request.POST and request.POST["passwordless"] == "1":
                # The user requested passwordless unlocks. Create new profile without a PIN.
                prof = Profile.objects.create(user=user, authToken=authToken)
                resp = {"message": "CREATED", "authToken": authToken}
                return HttpResponse(json.dumps(resp))

            pin = get_random_pin()
            # Create a new profile for the user.
            prof = Profile.objects.create(user=user, authToken=authToken, pin=pin)
            resp = {"message": "CREATED", "authToken": authToken, "pin": pin}
            return HttpResponse(json.dumps(resp))
        else:
            record_login_attempt(request, success=False)
            return HttpResponse(json.dumps({"message": "INV_CRED"}), status=401)
    else:
        return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)


@csrf_exempt
def authenticateView(request):
    """ Reads the AuthToken passed in from the user, along with the pin. If they both match exactly, start the unlock script. """
    # Originally coded by Thanos Ageridis
    if request.method == "POST":  # Same as above, only accept POST requests
        if "authToken" not in request.POST:  # Check if the AuthToken is inside the POST request.
            return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)
        else:
            givenauthtoken = request.POST["authToken"]
            if "pin" in request.POST:
                passwordless = False
                givenpin = request.POST["pin"]

                # Check the length of the PIN.
                # Note to self: NEVER do work when tired!
                if len(givenpin) != 6:
                    record_unlock_attempt(request, success=False)
                    return HttpResponse(json.dumps({"message": "UNAUTHORIZED"}), status=401)
            elif "wearToken" in request.POST:
                passwordless = True
                wear_unlock = True

                givenweartoken = request.POST["wearToken"]
            else:
                passwordless = True
                wear_unlock = False

            authenticated = False
            if passwordless and wear_unlock:
                if Profile.objects.filter(authToken=givenauthtoken, wearToken=givenweartoken).count() > 0:
                    authenticated = True
            elif passwordless and not wear_unlock:
                if Profile.objects.filter(authToken=givenauthtoken).count() > 0:
                    authenticated = True
            else:
                if Profile.objects.filter(pin=givenpin, authToken=givenauthtoken).count() > 0:
                    authenticated = True

            if authenticated:
                record_unlock_attempt(request, success=True, profile=Profile.objects.get(authToken=givenauthtoken))
                if not DEBUG:
                    # Make sure we unlock this only when debug mode is off.
                    unlock()
                return HttpResponse(json.dumps({"message": "SUCCESS"}), status=200)
            else:
                if Profile.objects.filter(authToken=givenauthtoken).count() > 0:
                    record_unlock_attempt(request, success=False, profile=Profile.objects.get(authToken=givenauthtoken))
                else:
                    record_unlock_attempt(request, success=False)
                return HttpResponse(json.dumps({"message": "UNAUTHORIZED"}), status=401)
    else:
        return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)

@csrf_exempt
def getWearToken(request):
    if request.method == "POST":
        if "authToken" not in request.POST or "pin" not in request.POST:
            return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)

        givenauthtoken = request.POST["authToken"]
        print givenauthtoken
        givenpin = request.POST["pin"]

        if Profile.objects.filter(authToken=givenauthtoken, pin=givenpin).count() > 0:
            prof = Profile.objects.filter(authToken=givenauthtoken, pin=givenpin).get()

            # If the Profile doesn't have a watch token, generate one and return it, else, get the already existing one.
            if prof.wearToken:
                return HttpResponse(json.dumps({"message": "SUCCESS", "wearToken": prof.wearToken}), status=200)
            else:
                prof.wearToken = get_watch_token()
                prof.save()
                return HttpResponse(json.dumps({"message": "SUCCESS", "wearToken": prof.wearToken}), status=200)
        else:
            return HttpResponse(json.dumps({"message": "UNAUTHORIZED"}), status=401)
    else:
        return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)

# NOTE: Access attempt tracking not possible yet for PIN changing.
@csrf_exempt
def changePin(request):
    if request.method == "POST":
        if "authToken" not in request.POST or "oldPin" not in request.POST or "newPin" not in request.POST:
            return HttpResponse(json.dumps({"message": "INV_REQ"}), status=400)
        else:
            token = request.POST["authToken"]
            oldpin = request.POST["oldPin"]
            newpin = request.POST["newPin"]

            # Check the length of both PINs.
            if len(oldpin) != 6 or len(newpin) != 6:
                return HttpResponse(json.dumps({"message": "UNAUTHORIZED"}), status=401)

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
        return HttpResponse(json.dumps({"status": "ALIVE", "version": getServerVersion()}))
    else:
        return HttpResponse(json.dumps({"status": "LOCKED", "version": getServerVersion()}))
