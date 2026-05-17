
from rest_framework_simplejwt.tokens import RefreshToken
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.hashers import (
    make_password,
    check_password
)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import User


# =========================
# REGISTER
# =========================

@csrf_exempt
def register(request):

    if request.method == "POST":

        data = json.loads(request.body)

        email = data.get("email")
        username = data.get("username")
        password = data.get("password")

        print("REGISTER WORKING")

        # ALLOW ONLY OCTOPUS EMAILS
        if not email.endswith("@octopus.com"):

            return JsonResponse({
                "success": False,
                "message": "Only octopus.com emails allowed"
            })

        # CHECK IF EMAIL EXISTS
        if User.objects.filter(email=email).exists():

            return JsonResponse({
                "success": False,
                "message": "Email already exists"
            })

        # CHECK IF USERNAME EXISTS
        if User.objects.filter(username=username).exists():

            return JsonResponse({
                "success": False,
                "message": "Username already exists"
            })

        # HASH PASSWORD
        hashed_password = make_password(password)

        # PRINT HASH
        print("ORIGINAL PASSWORD:", password)
        print("HASHED PASSWORD:", hashed_password)

        # CREATE USER
        User.objects.create(
            email=email,
            username=username,
            password=hashed_password
        )

        return JsonResponse({
            "success": True,
            "message": "Account created"
        })

    return JsonResponse({
        "success": False,
        "message": "Only POST method allowed"
    })


# =========================
# LOGIN
# =========================

@csrf_exempt
def login(request):

    if request.method == "POST":

        data = json.loads(request.body)

        email = data.get("email")
        password = data.get("password")

        try:

            user = User.objects.get(email=email)

            # CHECK HASHED PASSWORD
            valid = check_password(
                password,
                user.password
            )

            if valid:

                # CREATE JWT TOKEN
                refresh = RefreshToken.for_user(user)

                return JsonResponse({

                    "success": True,

                    "message": "Login successful",

                    "token": str(refresh.access_token),

                    "user": {

                        "id": user.id,

                        "email": user.email
                    }
                })

            return JsonResponse({
                "success": False,
                "message": "Wrong password"
            })

        except User.DoesNotExist:

            return JsonResponse({
                "success": False,
                "message": "User not found"
            })

    return JsonResponse({
        "success": False,
        "message": "Only POST method allowed"
    })


# =========================
# PROTECTED PROFILE
# =========================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):

    user = request.user

    return JsonResponse({
        "success": True,
        "message": "Protected route working",
        "user": {
            "id": user.id,
            "email": user.email
        }
    })