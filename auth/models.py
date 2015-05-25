from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone

class User(AbstractBaseUser):
    # Meta information
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['kind']

    # Choices
    ADMIN = 'A'
    STATION = 'S'
    SUPERVISOR = 'V'

    KIND_CHOICES = (
        (ADMIN, 'Administrator'),
        (STATION, 'Station staff'),
        (SUPERVISOR, 'Supervisor'),
    )

    username = models.CharField(max_length=32, unique=True)
    kind = models.CharField(max_length=1, choices=KIND_CHOICES)
    description = models.CharField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '<User: {}>'.format(self.username)

class Station(models.Model):
    name = models.CharField(max_length=16)
    user = models.OneToOneField(User)
    external_id = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    max_sessions = models.IntegerField()

    def __str__(self):
        return '<Station: {}>'.format(self.name)

class Session(models.Model):
    NORMAL = 'N'
    EXPIRED = 'E'
    NOT_RESPONDING = 'H'

    station = models.OneToOneField(Station)
    token = models.CharField(max_length=256, unique=True)
    created_on = models.DateTimeField(default=timezone.now)
    expired_on = models.DateTimeField()
    last_seen = models.DateTimeField(default=timezone.now)

    @property
    def status(self):
        now = timezone.now()
        if (now - self.last_seen) > settings.SESSION_MAX_RESPOND_TIME:
            return Session.NOT_RESPONDING
        elif self.expired_on > now:
            return Session.EXPIRED
        return Session.NORMAL

    def __str__(self):
        return '<Session: {}>'.format(self.created_on)