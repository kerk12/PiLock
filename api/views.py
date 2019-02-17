from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import render

# Create your views here.
from passlib.handlers.pbkdf2 import pbkdf2_sha512
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions, response

from main.models import Profile
from main.views import record_login_attempt, get_auth_token, get_random_pin, record_unlock_attempt


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            username = request.POST["username"]
            password = request.POST["password"]
        except KeyError:
            raise exceptions.ValidationError({'login':'Username and password expected.'})

        user = authenticate(username=username,
                            password=password)

        if user is not None:
            record_login_attempt(request, success=True)
            if Profile.objects.filter(user=user).count() > 0:
                raise exceptions.NotAuthenticated()

            token = get_auth_token()
            token_crypt = pbkdf2_sha512.hash(token)

            pin = get_random_pin()
            pin_crypt = pbkdf2_sha512.hash(pin)

            prof = Profile(user=user, authToken=token_crypt, pin=pin_crypt)
            prof.save()
            return Response({
                "message": "CREATED",
                "token": token,
                "pin": pin,
                "profile_id": prof.pk
                })

        else:
            record_login_attempt(request, success=False)
            raise exceptions.AuthenticationFailed()

class Authenticate(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            token = request.POST["token"]
            profile_id = request.POST["profile_id"]
        except KeyError:
            raise exceptions.ValidationError({'authentication':'token and profile_id expected.'})

        try:
            profile = Profile.objects.get(pk=profile_id)
        except Profile.DoesNotExist:
            raise exceptions.AuthenticationFailed()

        if not pbkdf2_sha512.verify(token, profile.authToken):
            record_unlock_attempt(request, success=False)
            raise exceptions.AuthenticationFailed()

        authenticated = False
        if profile.wearToken:

            try:
                wear_token = request.POST["wear_token"]
            except KeyError:
                raise exceptions.AuthenticationFailed()

            # Handle a wear unlock.
            if pbkdf2_sha512.verify(wear_token, profile.wearToken):
                authenticated = True
            else:
                record_unlock_attempt(request, success=False, profile=profile)
                raise exceptions.AuthenticationFailed()

        else:
            try:
                pin = request.POST["pin"]
            except KeyError:
                raise exceptions.AuthenticationFailed()

            if pbkdf2_sha512.verify(pin, profile.pin):
                authenticated = True
            else:
                record_unlock_attempt(request, success=False, profile=profile)
                raise exceptions.AuthenticationFailed()

        if not settings.DEBUG:
            from main.PiLockUnlockScripts.unlock import unlock
            # Make sure we unlock this only when debug mode is off.
            unlock()

        return Response({"message": "SUCCESS"})