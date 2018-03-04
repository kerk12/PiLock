import random
import string

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, Client, override_settings

def login(obj):
    req = obj.c.post("/login", data={"username": "testUser", "password": "1234asdf"})

    obj.assertEqual(req.status_code, 200)
    resp = req.json()

    obj.assertEqual(resp["message"], "CREATED")

    return resp["pin"], resp["authToken"], resp["device_profile_id"]

# Create your tests here.
@override_settings(DEBUG=True)
class PiLockMainTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testUser", password="1234asdf")
        self.user.save()

        self.c = Client()

    def test_unlock(self):
        pin, authToken, device_profile_id = login(self)

        # Try unlocking.
        req = self.c.post("/authentication",
                          data={"authToken": authToken, "pin": pin,
                                "device_profile_id": device_profile_id})

        self.assertEqual(req.status_code, 200)
        resp = req.json()

        self.assertEqual(resp["message"], "SUCCESS")

    def test_unlock_inv_creds(self):
        pin, authToken, device_profile_id = login(self)

        # Invalid authToken
        req = self.c.post("/authentication",
                          data={"authToken": authToken.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(10)),
                                "pin": pin,
                                "device_profile_id": device_profile_id})
        self.assertEqual(req.status_code, 401)
        resp = req.json()
        self.assertEqual(resp["message"], "UNAUTHORIZED")


        # Invalid PIN, correct authToken
        req = self.c.post("/authentication",
                          data={"authToken": authToken, "pin": ''.join(random.choice(string.digits) for _ in range(6)),
                                "device_profile_id": device_profile_id})
        self.assertEqual(req.status_code, 401)
        resp = req.json()
        self.assertEqual(resp["message"], "UNAUTHORIZED")

        # Invalid device_profile_id
        req = self.c.post("/authentication",
                          data={"authToken": authToken, "pin": ''.join(random.choice(string.digits) for _ in range(6)),
                                "device_profile_id": ''.join(random.choice(string.digits) for _ in range(3))})
        self.assertEqual(req.status_code, 401)
        resp = req.json()
        self.assertEqual(resp["message"], "UNAUTHORIZED")

        # Random PIN with random length
        req = self.c.post("/authentication",
                          data={"authToken": authToken, "pin": ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 100))),
                                "device_profile_id": device_profile_id})
        self.assertEqual(req.status_code, 401)
        resp = req.json()
        self.assertEqual(resp["message"], "UNAUTHORIZED")

    def test_invalid_login(self):
        req = self.c.post("/login", data={"username": "testUser", "password": "".join(random.choice(string.ascii_letters) for _ in range(random.randint(0,100)))})

        self.assertEqual(req.status_code, 401)
        resp = req.json()

        self.assertEqual(resp["message"], "INV_CRED")

