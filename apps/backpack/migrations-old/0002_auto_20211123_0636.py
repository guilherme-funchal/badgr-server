# Generated by Django 2.2.24 on 2021-11-23 14:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('backpack', '0001_initial'),
        ('issuer', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='backpackcollectionbadgeinstance',
            name='badgeinstance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issuer.BadgeInstance'),
        ),
        migrations.AddField(
            model_name='backpackcollectionbadgeinstance',
            name='badgeuser',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='backpackcollectionbadgeinstance',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backpack.BackpackCollection'),
        ),
        migrations.AddField(
            model_name='backpackcollection',
            name='assertions',
            field=models.ManyToManyField(blank=True, through='backpack.BackpackCollectionBadgeInstance', to='issuer.BadgeInstance'),
        ),
        migrations.AddField(
            model_name='backpackcollection',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='backpackcollection',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='backpackbadgeshare',
            name='badgeinstance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='issuer.BadgeInstance'),
        ),
    ]