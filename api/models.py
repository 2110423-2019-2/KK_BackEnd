from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class ExtendedUser(models.Model):
    isVerified = models.BooleanField(default=False)
    base_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='extended',
    )
    ban_list = models.ManyToManyField(
        User,
        related_name='banned',
        blank=True,
    )
    phone_number = models.CharField(
        validators=[
            RegexValidator(regex=r'^0\d{8,9}$'),
        ],
        max_length=12,
        blank=True,
    )

    def __str__(self):
        return self.base_user.username

    class Meta:
        unique_together = (('base_user',),)


class Court(models.Model):
    isVerified = models.BooleanField(default=False)
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='court',
    )
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Log(models.Model):
    user = models.ForeignKey(
        User,
        related_name='logs',
        on_delete=models.SET_NULL,
        null=True,
    )
    desc = models.CharField(max_length=50)

    def __str__(self):
        return '%s %s' % (self.user.username, self.desc, )
