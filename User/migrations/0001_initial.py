# Generated by Django 5.0.7 on 2024-12-07 14:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone', models.CharField(max_length=11)),
                ('address', models.CharField(max_length=100)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('amount', models.IntegerField(blank=True, default=0, null=True)),
                ('membership_start_date', models.DateTimeField(blank=True, null=True)),
                ('membership_end_date', models.DateTimeField(blank=True, null=True)),
                ('is_premium', models.BooleanField(default=False)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='images/profile_pictures/')),
                ('is_seller', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_sum', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_ratings', models.PositiveIntegerField(default=0)),
                ('total_properties', models.PositiveIntegerField(default=0)),
                ('average_rating', models.DecimalField(decimal_places=1, default=0.0, max_digits=2)),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='User.profile')),
            ],
        ),
    ]
