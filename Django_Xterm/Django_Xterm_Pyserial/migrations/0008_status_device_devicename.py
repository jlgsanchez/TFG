# Generated by Django 3.1 on 2021-12-01 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Django_Xterm_Pyserial', '0007_remove_group_device'),
    ]

    operations = [
        migrations.AddField(
            model_name='status_device',
            name='DeviceName',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
