# Generated by Django 5.0.6 on 2024-06-02 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0002_booking_additional_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('canceled', 'Canceled')], default='pending', max_length=20),
        ),
    ]