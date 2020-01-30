# Generated by Django 3.0.2 on 2020-01-30 14:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extendeduser',
            name='ban_list',
            field=models.ManyToManyField(blank=True, related_name='banned', to=settings.AUTH_USER_MODEL),
        ),
    ]
