# Generated by Django 5.1.2 on 2024-11-18 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userEx', '0014_alter_mediauploads_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='positioninformation',
            name='preferred_shift',
            field=models.CharField(blank=True, choices=[('Day', 'Day Shift'), ('Night', 'Night Shift'), ('6am - 12pm', '6am - 12pm'), ('12pm - 6pm', '12pm - 6pm'), ('6pm - 12am', '6pm - 12am')], max_length=20, null=True),
        ),
    ]
