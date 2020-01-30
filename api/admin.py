from django.contrib import admin
from .models import ExtendedUser, Court, Log

# Register your models here.
admin.site.register(ExtendedUser)
admin.site.register(Court)
admin.site.register(Log)
