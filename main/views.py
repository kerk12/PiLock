from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import random
import json
from django.contrib.auth import authenticate, login, logout
from .models import Profile, AccessAttempt
from .PiLockUnlockScripts.unlock import unlock
import os, sys
from PiLock.settings import getServerVersion, getRoot, BASE_DIR, DEBUG
from django.utils.crypto import get_random_string
import yaml
from ipware.ip import get_ip
from passlib.hash import pbkdf2_sha512
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
            return JsonResponse({"message": "INV_REQ"}, status=400)

        if len(request.POST["username"]) > 150:
            return JsonResponse({"message": "INV_REQ"}, status=400)

        user = authenticate(username=request.POST["username"],
                            password=request.POST["password"])  # Authenticate the user

        if user is not None:
            record_login_attempt(request, success=True)
            if Profile.objects.filter(user=user).count() > 0:
                # Check if the profile already exists
                return JsonResponse({"message": "PROFILE_REGISTERED"})
            # Generate new random auth token
            authToken = get_auth_token()
            authToken_crypt = pbkdf2_sha512.hash(authToken)

            if "passwordless" in request.POST and request.POST["passwordless"] == "1":
                # The user requested passwordless unlocks. Create new profile without a PIN.
                prof = Profile.objects.create(user=user, authToken=authToken_crypt)
                resp = {"message": "CREATED", "authToken": authToken, "device_profile_id":prof.id}
                return JsonResponse(resp)

            pin = get_random_pin()
            pin_crypt = pbkdf2_sha512.hash(pin)
            # Create a new profile for the user.
            prof = Profile.objects.create(user=user, authToken=authToken_crypt, pin=pin_crypt)
            resp = {"message": "CREATED", "authToken": authToken, "pin": pin, "device_profile_id":prof.id}
            return JsonResponse(resp)
        record_login_attempt(request, success=False)
        return JsonResponse(json.dumps({"message": "INV_CRED"}), status=401)
    else:
        return JsonResponse(json.dumps({"message": "INV_REQ"}), status=400)


@csrf_exempt
def authenticateView(request):
    """ Reads the AuthToken passed in from the user, along with the pin. If they both match exactly, start the unlock script. """
    # Originally coded by Thanos Ageridis
    if request.method == "POST":  # Same as above, only accept POST requests
        if "authToken" not in request.POST or "device_profile_id" not in request.POST:  # Check if the AuthToken and the ID is inside the POST request.
            return JsonResponse({"message": "INV_REQ"}, status=400)
        else:
            givenid = request.POST["device_profile_id"]
            givenauthtoken = request.POST["authToken"]
            if "pin" in request.POST:
                passwordless = False
                givenpin = request.POST["pin"]

                # Check the length of the PIN.
                # Note to self: NEVER do work when tired!
                if len(givenpin) != 6:
                    record_unlock_attempt(request, success=False)
                    return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
            elif "wearToken" in request.POST:
                passwordless = True
                wear_unlock = True

                givenweartoken = request.POST["wearToken"]
            else:
                passwordless = True
                wear_unlock = False

            authenticated = False
            profile = Profile.objects.filter(id=givenid)
            prof_count = profile.count()
            if prof_count > 0:
                profile = profile.get()
                if passwordless and wear_unlock:
                    if pbkdf2_sha512.verify(givenauthtoken, profile.authToken) and pbkdf2_sha512.verify(givenweartoken, profile.wearToken):
                        authenticated = True
                elif passwordless and not wear_unlock:
                    if pbkdf2_sha512.verify(givenauthtoken, profile.authToken):
                        authenticated = True
                else:
                    if pbkdf2_sha512.verify(givenpin, profile.pin) and pbkdf2_sha512.verify(givenauthtoken, profile.authToken):
                        authenticated = True

            if authenticated:
                record_unlock_attempt(request, success=True, profile=profile)
                if not DEBUG:
                    # Make sure we unlock this only when debug mode is off.
                    unlock()
                return JsonResponse({"message": "SUCCESS"}, status=200)
            else:
                if prof_count > 0:
                    record_unlock_attempt(request, success=False, profile=profile)
                else:
                    record_unlock_attempt(request, success=False)
                return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
    else:
        return JsonResponse({"message": "INV_REQ"}, status=400)

@csrf_exempt
def getWearToken(request):
    if request.method == "POST":
        if "authToken" not in request.POST or "pin" not in request.POST or "device_profile_id" not in request.POST:
            return JsonResponse({"message": "INV_REQ"}, status=400)

        givenauthtoken = request.POST["authToken"]
        print(givenauthtoken)
        givenpin = request.POST["pin"]
        givenid = request.POST["device_profile_id"]
        profile = Profile.objects.filter(id=givenid)
        if profile.count() > 0:
            prof = profile.get()
            if pbkdf2_sha512.verify(givenauthtoken, prof.authToken) and pbkdf2_sha512.verify(givenpin, prof.pin):
                wearToken = get_watch_token()
                wearToken_crypt = pbkdf2_sha512.hash(wearToken)
                prof.wearToken = wearToken_crypt

                prof.save()
                return JsonResponse({"message": "SUCCESS", "wearToken": wearToken}, status=200)
            else:
                return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
        else:
            return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
    else:
        return JsonResponse({"message": "INV_REQ"}, status=400)

# NOTE: Access attempt tracking not possible yet for PIN changing.
@csrf_exempt
def changePin(request):
    if request.method == "POST":
        if "device_profile_id" not in request.POST or "authToken" not in request.POST or "oldPin" not in request.POST or "newPin" not in request.POST:
            return JsonResponse({"message": "INV_REQ"}, status=400)
        else:
            givenid = request.POST["device_profile_id"]
            token = request.POST["authToken"]
            oldpin = request.POST["oldPin"]
            newpin = request.POST["newPin"]

            # Check the length of both PINs.
            if len(oldpin) != 6 or len(newpin) != 6:
                return JsonResponse(json.dumps({"message": "UNAUTHORIZED"}), status=401)

            #Searching for a profile with id matching the given id from the POST request.
            profile = Profile.objects.filter(id=givenid)
            if profile.count() > 0:
                profile = profile.get()
                if pbkdf2_sha512.verify(token, profile.authToken) and pbkdf2_sha512.verify(oldpin, profile.pin):
                    profile.pin = pbkdf2_sha512.hash(newpin)
                    profile.save()
                    return JsonResponse({"message": "SUCCESS"}, status=200)
                else:
                    return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
            else:
                return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
    else:
        return JsonResponse({"message": "INV_REQ"}, status=400)


def index(request):
    # return render(request, 'index.html', context)
    # Returns response with server's status (AKA: Heartbeat)
    if ReadConfig()["enabled"]:
        return JsonResponse({"status": "ALIVE", "version": getServerVersion()})
    else:
        return JsonResponse({"status": "LOCKED", "version": getServerVersion()})
