# Generated by Django 5.1.3 on 2025-01-01 19:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0031_alter_ordonnance_id_patient'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordonnance',
            name='id_patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Ordonnance', to=settings.AUTH_USER_MODEL),
        ),
    ]