# Generated by Django 3.0.2 on 2020-01-31 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20200131_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='price',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
