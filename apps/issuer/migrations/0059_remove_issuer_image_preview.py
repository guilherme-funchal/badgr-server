# Generated by Django 2.2.24 on 2021-09-23 14:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0058_auto_20210302_1103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issuer',
            name='image_preview',
        ),
    ]