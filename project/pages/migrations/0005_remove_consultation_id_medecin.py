# Generated by Django 5.1.3 on 2024-12-30 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_alter_rdv_id_patient_alter_rdv_id_secretaire'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consultation',
            name='id_medecin',
        ),
    ]