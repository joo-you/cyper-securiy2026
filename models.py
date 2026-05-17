from django.db import models
from django.conf import settings

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

# =========================
# USER MANAGER
# =========================

class UserManager(BaseUserManager):

    def create_user(
        self,
        email,
        username,
        password=None
    ):

        if not email:

            raise ValueError(
                "Email is required"
            )

        email = self.normalize_email(
            email
        )

        user = self.model(

            email=email,

            username=username
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        username,
        password
    ):

        user = self.create_user(

            email=email,

            username=username,

            password=password
        )

        user.is_staff = True

        user.is_superuser = True

        user.is_active = True

        user.save(using=self._db)

        return user


# =========================
# USER MODEL
# =========================

class User(
    AbstractBaseUser,
    PermissionsMixin
):

    email = models.EmailField(
        unique=True
    )

    username = models.CharField(

        max_length=100,

        unique=True
    )

    profile_image = models.ImageField(

        upload_to="profiles/",

        null=True,

        blank=True
    )

    is_online = models.BooleanField(
        default=False
    )

    last_seen = models.DateTimeField(

        null=True,

        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    def __str__(self):

        return self.email


# =========================
# CONVERSATION MODEL
# =========================

class Conversation(models.Model):

    participants = models.ManyToManyField(

        settings.AUTH_USER_MODEL,

        related_name="conversations"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return f"Conversation {self.id}"


# =========================
# MESSAGE MODEL
# =========================

class Message(models.Model):

    conversation = models.ForeignKey(

        Conversation,

        on_delete=models.CASCADE,

        related_name="messages"
    )

    sender = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE
    )

    text = models.TextField()

    encrypted = models.BooleanField(
        default=True
    )

    seen = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["created_at"]

    def __str__(self):

        return (
            f"{self.sender.email} : "
            f"{self.text[:20]}"
        )