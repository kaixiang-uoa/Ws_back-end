# Generated by Django 5.0.6 on 2024-06-02 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Events', '0005_alter_event_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]
