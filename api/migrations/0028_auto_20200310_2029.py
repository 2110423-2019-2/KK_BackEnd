# Generated by Django 3.0.4 on 2020-03-10 13:29

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0027_booking_court'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='price',
            field=models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shuttlecock',
            name='remaining',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ReserveRacket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reserve_date', models.DateTimeField(auto_now=True)),
                ('count', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('racket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reserveRacket', to='api.Racket')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reserveRacket', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
